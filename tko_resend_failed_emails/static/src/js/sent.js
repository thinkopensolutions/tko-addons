odoo.define('tko_resend_failed_emails.sent', function(require) {
    "use strict";

    var core = require('web.core');
    var session = require('web.session');
    var chat_manager = require('mail_base.base').chat_manager;
    var ChatThread = require('mail.ChatThread');
    var chat_manager = require('mail.chat_manager');
    var _lt = core._lt;
    var rpc = require('web.rpc');
    var ChatAction = core.action_registry.get('mail.chat.instant_messaging');

    ChatThread.include({

        thread_reload: function(message_id) {
            //TODO: reload thread
            //        this.render();
            var domain = [
                ['sent_failed', '=', true],
                ['sent', '=', true],
                ['author_id.user_ids', 'in', [session.uid]]
            ]
            return this._rpc({
                model: 'mail.message',
                method: 'message_fetch',
                args: [domain],
                kwargs: {
                    limit: 20,
                    context: session.user_context
                },
            }).then(function(msgs) {
                var messages = _.map(msgs, chat_manager.make_message);
                chat_manager.invalidate_caches(msgs.channel_ids);
                self.options.display_order = 1;
                self.render(messages, self.options)
                var channel = chat_manager.get_channel('channel_sent_failed');
                if (channel) {
//                    Reset cache with messages
//                      because clicking the menu again will load messages from cache
                    channel.cache['[]'].messages = messages;
               }
            })


        },

        message_resend: function(message_id) {
            self = this;
            var context = session.user_context;
            context.message_id = message_id;
            return rpc.query({
                    model: 'mail.message',
                    method: 'resend_failed_emails',
                    args: [{
                        'message_id': message_id
                    }],
                    context: context,
                })
                .then(function(result) {
                    self.thread_reload(message_id)
                });
        },
        start: function() {
            this._super.apply(this, arguments);
            this.sent_failed = this.options.sent_failed;

        },


        init: function(parent, options) {

            this._super.apply(this, arguments);
            // Add click reaction in the events of the thread object
            this.events['click .o-resend'] = function(event) {
                var message_id = $(event.currentTarget).data('message-id');
                this.message_resend(message_id);
                //                $(event.currentTarget).parent().parent().parent().parent().hide()
                //                this.trigger("message_resend", message_id);
            };
        },
    });

    ChatAction.include({
        init: function(parent, action, options) {
            this._super.apply(this, arguments);
            var channel_name = 'channel_sent_failed';
            this.sent_failed = this.options.sent_failed;
            // Add channel Sent for show "Send message" button
            this.channels_show_send_button.push(channel_name);
            // Add channel Sent for enable "display_subject" option
            this.channels_display_subject.push(channel_name);
            this.domain = [
                ['sent_failed', '=', true],
                ['sent', '=', true],
                ['author_id.user_ids', 'in', [session.uid]]
            ];
        },

        update_message_on_current_channel: function(current_channel_id, message) {
            var result = this._super.apply(this, arguments);
            var sent_failed = current_channel_id === "channel_sent_failed" && !message.sent_failed;
            return sent_failed || result;
        },

    });

    // Inherit class and override methods
    var chat_manager_super = _.clone(chat_manager);
    chat_manager.get_properties = function(msg) {
        var properties = chat_manager_super.get_properties.apply(this, arguments);
        properties.sent_failed = this.property_descr("channel_sent_failed", msg, this);
        return properties;
    };

    chat_manager.set_channel_flags = function(data, msg) {
        chat_manager_super.set_channel_flags.apply(this, arguments);
        if (data.sent_failed && data.author_id[0] === session.partner_id) {
            msg.sent_failed = true;
        }
        return msg;
    };

    chat_manager.get_channel_array = function(msg) {
        var arr = chat_manager_super.get_channel_array.apply(this, arguments);
        return arr.concat('channel_sent_failed');
    };

    chat_manager.get_domain = function(channel) {
        return (channel.id === "channel_sent_failed") ?
            [
                ['sent_failed', '=', true],
                ['author_id.user_ids', 'in', [session.uid]]
            ] :
            chat_manager_super.get_domain.apply(this, arguments);
    };


    chat_manager.is_ready.then(function() {
        // Add sent channel
        chat_manager.add_channel({
            id: "channel_sent_failed",
            name: _lt("Sent Failed"),
            type: "static"
        });
        return $.when();
    });

    return chat_manager;

});