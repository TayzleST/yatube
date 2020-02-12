from django.test import TestCase, Client
from .models import Post, User
import datetime as dt


class PlansPageTest(TestCase):
    # название класса скопировал из тренажера
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="sarah",\
                    email="connor.s@skynet.com", password="12345")
        self.post = Post.objects.create(text='hello,vsem', author=self.user)
        
        
    def testPageCodes(self):
        response = self.client.post('')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/admin/')
        self.assertEqual(response.status_code, 302)

    def testIndexContext(self):
        response = self.client.get('')
        self.assertContains(response, text='hello,vsem', msg_prefix='You have NO posts')

    def testIndexTemplate(self):
        response = self.client.get('')
        self.assertTemplateUsed(response, template_name='index.html')

    def testContextProcessor(self):
        today = dt.datetime.today().year
        response = self.client.get('')
        self.assertEqual(response.context['year'], today)
        
        
        

