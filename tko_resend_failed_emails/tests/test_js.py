# -*- coding: utf-8 -*-
import odoo.tests


@odoo.tests.common.at_install(False)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):

    def test_01_tko_resend_failed_emails(self):
        # wait till page loaded and then click and wait again
        code = """
            setTimeout(function () {
                $(".tko_resend_failed_emails").click();
                setTimeout(function () {console.log('ok');}, 3000);
            }, 1000);
        """
        link = '/web#action=%s' % self.ref('mail.mail_channel_action_client_chat')
        self.phantom_js(link, code, "odoo.__DEBUG__.services['tko_resend_failed_emails.sent'].is_ready", login="demo")
