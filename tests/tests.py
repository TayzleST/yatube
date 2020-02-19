from django.test import TestCase, Client, RequestFactory
from django.core import mail
import datetime as dt
from django.shortcuts import render, redirect, get_object_or_404

from posts.models import Post, User
from users.views import SignUp

# Пользователь регистрируется и ему отправляется письмо с подтверждением регистрации
class EmailTest(TestCase):
    '''
    Проверка правильности заполнения письма об успешной регистрации
    '''
    def test_send_email(self):
        self.user = User.objects.create_user(username="sarah", 
                    email="connor.s@skynet.com", password="12345")
        email = self.user.email
        SignUp.send_email(self, email, first_name='first_name', last_name='last_name')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Регистрация пользователя')
        self.assertEqual(mail.outbox[0].body,
                        'last_name first_name, благодарим за регистрацию на нашем сайте!')
        self.assertEqual(mail.outbox[0].from_email, 'yatube@mail.ru')
        self.assertEqual(mail.outbox[0].to, [email])

class PostViewTest(TestCase):
    '''
    Проверка правильности отображения страниц при создании/редактировании постов
    '''
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
                         username="sarah", email="connor.s@skynet.com", password="12345"
                        )
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
        

        
 #Авторизованный пользователь может опубликовать пост (new)
     # проверить авторизацию
     # если авторизация успешна то ответ сраницы new/ 200
 #Неавторизованный посетитель не может опубликовать пост (его редиректит на страницу входа)
     # если авторизация НЕ успешна то ответ сраницы new/ 302 (redirect)
 #После публикации поста новая запись появляется на главной странице сайта (index), на персональной странице пользователя (profile), и на отдельной странице поста (post)
     # textContent на всех трех страницах
 #Авторизованный пользователь может отредактировать свой пост и его содержимое изменится на всех связанных страницах
     # для авторизованного пользователя доступна страница редактирована (нужно текущего пользователя выцепить)
     # для неаторизованного редиректит(ответ 302)
     # создать новый пост со страрым id и проверить 








#    def test_registration(self):
#        # проверка, что пользователь зарегистрировался
#        self.new_user = get_object_or_404(User, username='sarah')
#        print('hello')
#        self.assertEqual(self.new_user.email, 'connor.s@skynet.com')
#        response = self.client.post('/auth/login/', username="sarah", password="12345",)
#        print(response)
#        self.assertRedirects(response,"http://google.com",fetch_redirect_response=False )

        


    

#        request = self.factory.post('/auth/signup/', {'name': 'terminator', 'passwd': 'skynetMyLove', 'email': "connor.s@skynet.com"})
#        print(request.POST)
#        response = SignUp.as_view()(request)
#        print(response.status)
#        response = self.client.post('/auth/signup/', {'name': 'terminator', 'passwd': 'skynetMyLove', 'email': "connor.s@skynet.com"})
#        response = SignUp.as_view()(request)
#        print(response.client)
        # Проверяем, что письмо лежит в исходящих
#        self.assertEqual(len(mail.outbox), 1)
        # Проверяем, что тема первого письма правильная.
#        self.assertEqual(mail.outbox[0].subject, 'Регистрация пользователя')
#        print(mail.outbox)
#        print(mail.outbox[0].to)


#class PlansPageTest(TestCase):
#    # название класса скопировал из тренажера
#    def setUp(self):
#        self.client = Client()
# #       self.user = User.objects.create_user(username="sarah",\
#                    email="connor.s@skynet.com", password="12345")
#        self.post = Post.objects.create(text='hello,vsem', author=self.user)
        
        
#    def testPageCodes(self):
#        response = self.client.post('')
#        self.assertEqual(response.status_code, 200)

#        response = self.client.post('/admin/')
# #       self.assertEqual(response.status_code, 302)

#    def testIndexContext(self):
#        response = self.client.get('')
#        self.assertContains(response, text='hello,vsem', msg_prefix='You have NO posts')

#    def testIndexTemplate(self):
#        response = self.client.get('')
#        self.assertTemplateUsed(response, template_name='index.html')

#    def testContextProcessor(self):
#        today = dt.datetime.today().year
#        response = self.client.get('')
#        self.assertEqual(response.context['year'], today)