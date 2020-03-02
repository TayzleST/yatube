from django.test import TestCase, Client, RequestFactory
from django.core import mail
from django.urls import reverse
from django.conf import settings
import datetime as dt
from django.core.cache import cache
from django.core.cache.backends import locmem
from django.core.cache.utils import make_template_fragment_key

from posts.models import Post, User, Group, Follow
from users.views import SignUp
from posts.views import post_edit


# Пользователь регистрируется и ему отправляется письмо с подтверждением регистрации
class EmailTest(TestCase):
    '''
    Проверка регистрации и правильности заполнения письма об успешной регистрации
    '''
    
    def test_send_email(self):
        self.client = Client()
        # Проверка, что НЕ зарегистрированный пользователь не может залогиниться
        login = self.client.login(username='terminator', password='skynetMyLove')
        self.assertFalse(login)
        # создаем запрос методом POST с данными нового пользователя на страницу регистрации
        request = RequestFactory().post('/auth/signup/',
            {'username': 'terminator', 'email': 'terminator@mail.ru', 'password1': 'skynetMyLove',
             'password2': 'skynetMyLove', 'first_name': 'Sara', 'last_name': 'Conor'},
            follow=True)
        SignUp.as_view()(request)
        # Проверка, что новый пользователь зарегистрировался и может залогиниться
        login = self.client.login(username='terminator', password='skynetMyLove')
        self.assertTrue(login)
        # Проверка отправки почты и корректности введенных данных
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Регистрация пользователя')
        self.assertEqual(mail.outbox[0].body,
                        'Conor Sara, благодарим за регистрацию на нашем сайте!')
        self.assertEqual(mail.outbox[0].from_email, 'yatube@mail.ru')
        self.assertEqual(mail.outbox[0].to, ['terminator@mail.ru'])
    

class PostViewTest(TestCase):
    '''
    Проверка правильности отображения страниц при создании/редактировании постов
    '''
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="sarah", 
                                             email="connor.s@skynet.com", password="12345")
        self.post = Post.objects.create(text="It's driving me crazy!", author=self.user)
    
    def tearDown(self):
        cache.clear()

    #Проверка, что после регистрации пользователя создается его персональная страница (profile)
    def test_profile_after_signup(self):
        # для зарегистрированного пользователя ответ 200 для его персональной странцы
        response = self.client.get('/sarah/')
        self.assertEqual(response.status_code, 200)
        # персональная страница содержит имя зарегистрированного пользователя
        self.assertContains(response, text='sarah', 
                            msg_prefix='не отображается имя пользователя на странице профиля')
        # в контекст передан правильный пользователь
        self.assertIsInstance(response.context['profile'], User)
        self.assertEqual(response.context['profile'].username, 'sarah')
        # если пользователь не зарегистрирован, его страницы не сущестует (ответ 404)
        response = self.client.get('/unknown/')
        self.assertEqual(response.status_code, 404)
        

    #Проверка, что авторизованный пользователь может опубликовать пост (new)
    def test_logged_in_user_can_create_post(self):
        # залогинем sarah
        self.client.login(username='sarah', password='12345')
        response = self.client.get('/new/')
        # ответ при переходе на страницу нового поста должен быть 200
        self.assertEqual(response.status_code, 200)

    #Проверка, что неавторизованный посетитель не может опубликовать пост 
    # (его редиректит на страницу входа)
    def test_not_logged_in_cant_create_post(self):
        # sarah НЕ залогинена, должен быть код 302 и редирект в '/'
        response = self.client.get('/new/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/auth/login/?next=/new/',)


    # Проверка, что после публикации поста новая запись появляется на 
    # главной странице сайта (index), на персональной странице пользователя (profile),
    # и на отдельной странице поста (post)
    def test_post_displayed_on_all_pages(self):          
        ''' метод assertContains НЕ может искать выражения с апострофом, поэтому здесь используется
            assertEqual и искомое выражение вытаскиваем из контекста. Пример работы с assertContains
            будет показана ниже в тесте test_post_edit
        '''
        # проверяем отображение поста на главной странице (index)
        response = self.client.get('/')
        self.assertEqual(str(response.context['paginator'].object_list[0]), "It's driving me crazy!")
        # проверяем отображение поста на персональной странице пользователя (profile)
        response = self.client.get('/sarah/')
        self.assertEqual(str(response.context['paginator'].object_list[0]), "It's driving me crazy!")
        # проверяем отображение поста на отдельной странице поста (post)
        response = self.client.get(reverse('post', args=['sarah', 1]))
        self.assertEqual(str(response.context['post']), "It's driving me crazy!")

    
    # Проверка, что авторизованный пользователь может отредактировать свой пост
    # и его содержимое изменится на всех связанных страницах
    def test_post_edit(self):
        ''' 
        В этом тесте используется assertContains для поиска выражения
        '''
        # залогинем sarah
        self.client.login(username='sarah', password='12345')
        # создаем запрос методом POST к редактируемой странице с измененным текстом 
        '''
        Альтернативный рабочий метод через RequestFactory()
        request = RequestFactory().post('/sarah/1/edit/', {'text': "I ll be back!"}, follow=True)
        request.user = self.user
        post_edit(request, username='sarah', post_id=1)
        Ниже вариант через Client()
        '''
        self.client.post(reverse('post_edit', kwargs={'username': 'sarah', 'post_id': 1}),
                                {'text': "I ll be back!"}, follow=True)
        # проверяем изменение поста на главной странице (index)
        response = self.client.get('/')
        self.assertContains(response, "I ll be back!")
        # проверяем изменение поста на персональной странице пользователя (profile)
        response = self.client.get('/sarah/')
        self.assertContains(response, "I ll be back!")
        # проверяем изменение поста на отдельной странице поста (post)
        response = self.client.get(reverse('post', args=['sarah', 1]))
        self.assertContains(response, "I ll be back!")


class Error404Test(TestCase):
    '''
    Проверка, возвращает ли сервер 404, если страница не найдена
    '''
    def test_404_code(self):
        # проверяем что ответ сервера 404, если страница не найдена
        self.client = Client()
        response = self.client.get('/404/')
        self.assertEqual(response.status_code, 404)
        # проверка используется ли нужный темплейт, если DEBUG=False
        if settings.DEBUG == False:
            self.assertTemplateUsed(response, template_name='misc/404.html',)
        # проверка, передана ли в контекст переменная path
            self.assertEqual(response.context['path'], '/404/')

class FooterTest(TestCase):
    '''
    Проверка что в подвал сайта выводится правильная дата
    '''
    def testContextProcessor(self):
        # проверяем дату
        today = dt.datetime.today().year
        response = self.client.get('/')
        self.assertEqual(response.context['year'], today)
        # проверяем исползование нужного темплейта
        self.assertTemplateUsed(response, template_name='footer.html',)
    
class ImageTest(TestCase):
    '''
    Проверка правильности отображения картинок на страницах
    '''
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="sarah", 
                                             email="connor.s@skynet.com", password="12345")
        self.group = Group.objects.create(slug='dogs', title='псы')
        self.post = Post.objects.create(text="It's driving me crazy!", author=self.user, group=self.group)
        # залогинем sarah
        self.client.login(username='sarah', password='12345')
    
    def tearDown(self):
        cache.clear()

    def test_image_on_pages(self):
        # проверим отсутствие картинки на главной странице, странице профайла,
        # странице группы и странице конкретной записи.
        response = self.client.get('/') # главная страница
        self.assertNotContains(response, text='<img')
        response = self.client.get('/sarah/') # страница профайла
        self.assertNotContains(response, text='<img')
        response = self.client.get('/group/dogs/') # страница группы
        self.assertNotContains(response, text='<img')
        response = self.client.get('/sarah/1/') # страница конкретной записи
        self.assertNotContains(response, text='<img')
        # дополнительная очистка кеша, иначе тесты ниже не увидят измененную страницу сайта
        cache.clear()
        # создадим новую запись с текстом и картинкой
        img = 'tests/for_image_testing/favicon.png'
        with open(img, 'rb') as fp:
            self.client.post('/new/', {'text': "I ll be back!", 'image': fp, 'group': 1,}, follow=True)
        # проверяем, что картинка появилась на всех страницах
        response = self.client.get('/') # главная страница
        self.assertContains(response, "I ll be back!") # на всякий случай проверим новый текст
        self.assertContains(response, text='<img')
        response = self.client.get('/sarah/') # страница профайла
        self.assertContains(response, text='<img')  
        response = self.client.get('/group/dogs/') # страница группы
        self.assertContains(response, text='<img') 
        response = self.client.get('/sarah/2/') # страница конкретной записи
        self.assertContains(response, text='<img')


    def test_valid_image(self):
        # проверка, что загрузить можно только картинки.
        # сначала загружаем картинку, должен произойти редирект(код 302)
        img = 'tests/for_image_testing/favicon.png'
        with open(img, 'rb') as fp:
            response = self.client.post('/new/', {'text': "I ll be back!", 'image': fp, 'title': 'псы'})
        # проверяем редирект
        self.assertEqual(response.status_code, 302)
        # для проверки защиты попробуем загрузить текстовый файл. 
        # Если защита сработает - не будет редиректа(код 200)
        img = 'tests/for_image_testing/test.txt'
        with open(img, 'rb') as fp:
            response = self.client.post('/new/', {'text': "I ll be back!", 'image': fp, 'title': 'псы'})
        self.assertEqual(response.status_code, 200)


class CacheTest(TestCase):
    '''
    Проверка кеширования страниц
    '''  
    def tearDown(self):
        cache.clear()

    def test_index_cache(self):
        # проверка, что главная страница кэшируется
        # проверяем, что в кеше ничего нет
        self.assertFalse(locmem._caches[''])
        # загружаем главную страницу и еще раз проверяем наличие кэша
        response = self.client.get('/') 
        self.assertTrue(locmem._caches[''])
        # проверяем, что ключ кэша соответстует установленному в index.html
        self.assertIn('.index_page.', str(list(locmem._caches[''])),
                    msg='Проверьте название ключа кэша. Ранее был установлен "index_page"')


    def test_index_cache_alternative_method(self):
        # второй способ, решил написать отдельно.
        key = make_template_fragment_key('index_page', [1]) # аргумент [1], так как в шаблоне 
                                                      # добавили номер страницы из паджинатора 
        self.assertFalse(cache.get(key))
        response = self.client.get('/')
        self.assertTrue(cache.get(key))


class FollowTest(TestCase):
    '''
    Проверка возможности подписываться на других авторов
    '''  
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
                    username="testuser1", email="test1@mail.ru", password="12345")
        self.user2 = User.objects.create_user(
                    username="testuser2", email="test2@mail.ru", password="23456")
        self.user3 = User.objects.create_user(
                    username="testuser3", email="test3@mail.ru", password="34567")
        self.post = Post.objects.create(text="It s driving me crazy!", author=self.user1)
        self.post = Post.objects.create(text="I ll be back", author=self.user2)

    def tearDown(self):
        cache.clear()

    # проверка, что aвторизованный пользователь может подписываться 
    # на других пользователей и удалять их из подписок.
    def test_following_to_other_author(self):
        # залогинем testuser1
        self.client.login(username='testuser1', password='12345')
        # проверяем, что в базе с подписками Follow нет записей
        self.assertEqual(Follow.objects.count(), 0)
        # подписываем testuser1 на testuser2
        response = self.client.get('/testuser2/follow', follow=True)
        self.assertRedirects(response, '/testuser2/')
        # проверяем, что в базе с подписками Follow появилась одна запись
        self.assertEqual(Follow.objects.count(), 1)
        # проверяем, что testuser1 подписался на testuser2, а не наоборот
        self.assertEqual(Follow.objects.get(id=1).user, self.user1)
        self.assertEqual(Follow.objects.get(id=1).author, self.user2)
        # testuser1 удаляет подписку на testuser2
        response = self.client.get('/testuser2/unfollow', follow=True)
        # проверяем, что в базе Follow не осталось записи
        self.assertEqual(Follow.objects.count(), 0)


    # проверка, что новая запись пользователя появляется в ленте тех,
    # кто на него подписан и не появляется в ленте тех, кто не подписан на него.    
    def test_post_for_following_user_only(self):
        # testuser 1 создает новую запись
        self.client.login(username='testuser1', password='12345')
        self.client.post('/new/', {'text': "Hello, world!"}, follow=True)
        # залогинем testuser2 и проверим, отобразилась ли запись 
        # пользователя testuser1 без подписки
        self.client.login(username='testuser2', password='23456')
        response = self.client.get('/follow/', follow=True)
        self.assertNotContains(response, text="Hello, world!") # НЕ отобразилась запись testuser1
        self.assertNotContains(response, text="I ll be back") # testuser2 НЕ должен видеть свою запись в ленте
        # если зайти на страницу со всеми авторами, testuser2 должен видеть обе записи
        response = self.client.get('/', follow=True)
        self.assertContains(response, text="Hello, world!") 
        self.assertContains(response, text="I ll be back") 
        # testuser2 подписывается на testuser1 и заходит на свою ленту
        self.client.get('/testuser1/follow', follow=True)
        response = self.client.get('/follow/', follow=True)
        # проверяем отображение старого и нового поста testuser1 на ленте testuser2
        self.assertContains(response, text="It s driving me crazy!")
        self.assertContains(response, text="Hello, world!")
        # проверяем отсутсвие своего поста на ленте подписки
        self.assertNotContains(response, text="I ll be back")
        
        # подпишем testuser3 на testuser2 и проверим, что у него
        # в ленте не отображается пост testuser1, а только пост testuser2
        self.client.login(username='testuser3', password='34567')
        # подпишем testuser3 на testuser2 и проверим ленту новостей testuser3
        self.client.get('/testuser2/follow',follow=True )
        response = self.client.get('/follow/', follow=True)
        # testuser3 НЕ должен видеть пост testuser1
        self.assertNotContains(response, text="Hello, world!")
        # testuser3 должен видеть пост testuser2
        self.assertContains(response, text="I ll be back")


class CommentTest(TestCase):
    '''
    Проверка возможности комментировать посты других авторов
    '''          
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
                    username="testuser1", email="test1@mail.ru", password="12345")
        self.user2 = User.objects.create_user(
                    username="testuser2", email="test2@mail.ru", password="23456")
        self.post = Post.objects.create(text="It s driving me crazy!", author=self.user1)

    def tearDown(self):
        cache.clear()

    # проверка, что только авторизированный пользователь может комментировать посты    
    def test_logged_in_user_comments_only(self):
        # пробуем без логина создать комментарий для поста testuser1
        response = self.client.post(reverse('add_comment', kwargs={'username': 'testuser1', 'post_id': 1}),
                                   {'text': "Hi, Sarah!"}, follow=True)
        # у незалогиненного пользователя должен произойти редирект на страницу логина
        self.assertRedirects(response, '/auth/login/?next=/testuser1/1/comment',)
        # залогинем testuser2 и повторим создание комментария
        self.client.login(username='testuser2', password='23456')
        response = self.client.post(reverse('add_comment', kwargs={'username': 'testuser1', 'post_id': 1}),
                                   {'text': "Hi, Sarah!"}, follow=True)
        # должен вернуться код 200
        self.assertEqual(response.status_code, 200,)
        # проверяем наличие поста и комментария к нему на странице поста
        response = self.client.get('/testuser1/1/')
        self.assertContains(response, text="It s driving me crazy!") # пост
        self.assertContains(response, text="Hi, Sarah!") # комментарий к нему