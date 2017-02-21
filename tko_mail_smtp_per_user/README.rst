SMTP Server Per User
====================
Configure Odoo to use specific incoming and outgoing email server by user.

## New in v2.0:

**Automatic outgoing SMTP mail server detection**: Through the [From] address of outgoing message, Odoo will select correct outgoing SMTP mail server to send email. This way if there is a SMTP mail server equal to the current user email, or equal to the [From] field in email template, Odoo will use that outgoing email server to send the email.

**Template compatible**: If one sets [From] field in the email template, Odoo will send that email from that outgoing SMTP server, if defined, if not it will use standard mail.catchall.alias system parameter and outgoing email servers by priority.

**NOTE**: Don't forget, you need now to set explicitly the [From] and [Reply-to] fields in email templates. And create always the incoming mail server of the respective outgoing one. The [Reply-to] will always be equal to [From] email (even if defined in template [Reply-to] field). If no outgoing email server is defined, it will use standard mail.catchall.alias system parameter, like in standard Odoo.

> **Backward compatibility**: All fields are kept in database, although not shown in forms, until new version is released. **No data will be lost**, and one can revert to older module version. NOTE: They will be removed in 3.0 version.

## **New in v1.0**:

The module set following email HEADERS according to user SMTP server:

- From: UserName SMTP_Server_User_Name_Email
- Reply-To: UserName SMTP_Server_User_Name_Email
- Return-Path: UserName SMTP_Server_User_Name_Email

This will fix a problem connecting to servers like for example Zoho. But will override email templates [From] and [Reply-to] definitions.

## **Configuration**:

To configure Odoo email gateway please consider this steps:

- Go to "Settings --> Technical --> General Settings" and set your domain in "Alias Domain" (ex: mydomain.com).
- Go to "Settings --> Technical --> Parameters --> System Parameters" and check if you have:

  - Parameter key "mail.catchall.domain" must be same domain you give above (ex: mydomain.com).
  - Parameter key "mail.catchall.alias" this is the catchall alias email (ex: catchall).
  - Parameter key "mail.bounce.alias" this is the bounce alias email (ex: bounce). The default bounce address is used to set the envelop address if no envelop address is provided in the message. It is formed by properly joining the parameters "mail.catchall.alias" and "mail.catchall.domain". If "mail.catchall.alias" is not set it defaults to "postmaster-odoo".

**NOTE:** use with care, some relay servers will not forward emails with no bounce email account configured and Odoo does this dynamically (ex: bounce-16-res_partner34@yourdomain.com). Catchall and bounce parameters can be the equal.

- Go to "Settings --> Technical --> Email --> Incoming Mail Servers", create catchall mail server (ex: catchall@mydomain.com)
- If you have bounce parameter, go to "Settings --> Technical --> Email --> Incoming Mail Servers", create bounce mail server (ex: bounce@mydomain.com)
- Go to "Settings --> Technical --> Email --> Incoming Mail Servers", create user mail server (ex: newuser@mydomain.com)
- Go to "Settings --> Technical --> Email --> Outgoing Mail Servers", create outgoing SMTP server (ex: newuser@mydomain.com). Select the user you previously created as owner.
- **CONGRATULATIONS**, you can now login as your new user and send emails, they will reach destination with the from and reply to as newuser@mydomain.com. And on reply you will get them in same entity from where you've sent it.
- You should create an income and outgoing email server for each user.
- You can **still use Odoo in the standard way**, and only some users having specific SMTP email server. It will only set the emails sent by users with specific email server.

Credits
=======

Contributors
------------

 * Carlos Almeida <carlos.almeida@tkobr.com>
 * Alexandre Rüffer <alexandre.ruffer@tkobr.com>

Maintainer
----------

![alt tag](http://tkobr.tkobr.com/logo.png)

This module is maintained by ThinkOpen Solutions.

To contribute to this module, please visit https://github.com/thinkopensolutions/tkobr-addons/issues.