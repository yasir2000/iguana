"""
Iguana (c) by Marc Ammon, Moritz Fickenscher, Lukas Fridolin,
Michael Gunselmann, Katrin Raab, Christian Strate

Iguana is licensed under a
Creative Commons Attribution-ShareAlike 4.0 International License.

You should have received a copy of the license along with this
work. If not, see <http://creativecommons.org/licenses/by-sa/4.0/>.
"""
from django.test.testcases import TestCase
from django.urls.base import reverse

from project.models import Project
from issue.models import Issue
from user_management.views import LoginView
from django.contrib.auth import get_user_model
from user_profile.views import ShowProfilePageView, EditProfilePageView, ToggleNotificationView
from common.testcases.generic_testcase_helper import view_and_template, redirect_to_login_and_login_required

user_name = "test"
test_password = "test1234"
test_email = "test@testing.com"


class ShowProfilePageTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # NOTE: if you modify these elements they need to be created in setUp(), instead of here
        cls.user = get_user_model().objects.create_user(user_name, test_email, test_password)

    def setUp(self):
        self.client.force_login(self.user)
        # NOTE: these elements get modified by some testcases, so they should NOT be created in setUpTestData()

    def test_view_and_template(self):
        # ShowProfilePageView
        view_and_template(self, ShowProfilePageView, 'user_profile/user_profile_page.html',
                          'user_profile:user_profile_page', address_kwargs={'username': user_name})
        # EditProfilePageView
        view_and_template(self, EditProfilePageView, 'user_profile/edit_user_profile.html',
                          'user_profile:edit_profile', address_kwargs={'username': user_name})

        # TODO TESTCASE - this needs to be post
        # view_and_template(self, ToggleNotificationView, 'user_profile/user_profile_page.html',
        #                   'user_profile:toggle_notification', address_kwargs={'username': user_name})
        #      - ...

    def test_redirect_to_login_and_login_required(self):
        self.client.logout()
        # ShowProfilePageView
        redirect_to_login_and_login_required(self, 'user_profile:user_profile_page',
                                             address_kwargs={"username": user_name})
        # EditProfilePageView
        redirect_to_login_and_login_required(self, 'user_profile:edit_profile',
                                             address_kwargs={"username": user_name})

        # TODO TESTCASE - this needs to be post
        # redirect_to_login_and_login_required(self, 'user_profile:toggle_notification',
        #                                      address_kwargs={"username": user_name})

    def test_show_other_user_profile_page(self):
        otheruser = get_user_model().objects.create_user('uname', 'umail@a.b', 'abcd')

        sharedproject = Project(creator=self.user, name_short='SPRJ')
        sharedproject.save()
        sharedproject.developer.add(self.user)
        sharedproject.developer.add(otheruser)
        notsharedproject = Project(creator=self.user, name_short='NPRJ')
        notsharedproject.save()
        notsharedproject.developer.add(self.user)

        sharedissue = Issue(title='abcd', project=sharedproject)
        sharedissue.save()
        sharedissue.assignee.add(self.user)
        sharedissue.assignee.add(otheruser)
        notsharedissue = Issue(title='efgh', project=sharedproject)
        notsharedissue.save()
        notsharedissue.assignee.add(self.user)

        response = self.client.get(reverse('user_profile:user_profile_page', kwargs={"username": otheruser.username}))
        self.assertContains(response, otheruser.username)
        self.assertContains(response, sharedproject)
        self.assertContains(response, sharedissue)
        self.assertNotIn(notsharedissue, response.context['sharedissues'])
        self.assertNotIn(notsharedproject, response.context['sharedprojects'])

    def test_show_user_profile_page(self):
        response = self.client.get(reverse('user_profile:user_profile_page', kwargs={"username": user_name}))
        self.assertContains(response, user_name)
