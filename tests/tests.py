from django.test import TestCase, Client, RequestFactory
from django.core import mail
from django.urls import reverse
from django.conf import settings


from posts.models import Post, User
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
        # залогинем sarah
        self.client.login(username='sarah', password='12345')
        # создаем запрос методом POST к редактируемой странице с измененным текстом 
        request = RequestFactory().post('/sarah/1/edit/', {'text': "I'll be back!"}, follow=True)
        request.user = self.user
        post_edit(request, username='sarah', post_id=1)
        # проверяем изменение поста на главной странице (index)
        response = self.client.get('/')
        self.assertEqual(str(response.context['paginator'].object_list[0]), "I'll be back!")
        # проверяем изменение поста на персональной странице пользователя (profile)
        response = self.client.get('/sarah/')
        self.assertEqual(str(response.context['paginator'].object_list[0]), "I'll be back!")
        # проверяем изменение поста на отдельной странице поста (post)
        response = self.client.get(reverse('post', args=['sarah', 1]))
        self.assertEqual(str(response.context['post']), "I'll be back!")


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
