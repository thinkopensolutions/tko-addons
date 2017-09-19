# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from openerp import tools
from openerp import models, fields, api, exceptions, _ 

class prisme_postit(models.Model):
    """ Post It data """
    _name = 'prisme.postit'
    _description = 'Prisme postit'
    _inherit = ['mail.thread']
	
    name= fields.Char(string="Name", required=True)
    names_users = fields.Char(string="Assigned to")
    description = fields.Text()
    assigned_by = fields.Many2one('res.users', string="Assigned by")
    assigned_to = fields.Many2many('res.users', 'prisme_postit_assignedto_rel', string="Assigned to")
    copy_to = fields.Many2many('res.users', 'prisme_postit_copyto_rel', string="Copy to")
    partner_id = fields.Many2one('res.partner', string="Client")
    priority = fields.Integer(string="Priority")
    tags = fields.Many2many('prisme.postit.tag', string="Tags")
    days = fields.Many2many('prisme.postit.day', string="Days")
    date_start = fields.Date(string="Date start")
    date_end = fields.Date(string="Date end")
    recall_date = fields.Date(string="Recall Date")
    duration = fields.Char(string='Duration')
    state= fields.Selection([('active', 'Non termine'),('get_started','Demarre'),('in_process','En cours'),('terminated', 'Termine'),], default='active')

    def init(self):
        self.env.cr.execute("""DROP TRIGGER IF EXISTS postit_update ON prisme_postit_assignedto_rel;""")
        self.env.cr.execute("""CREATE OR REPLACE FUNCTION postit_update() RETURNS trigger AS $$ BEGIN IF pg_trigger_depth() <> 1 THEN RETURN NEW; END IF; UPDATE prisme_postit SET names_users = subquery.string_agg FROM (SELECT ppar.prisme_postit_id,string_agg(partner.name, ', ') FROM prisme_postit_assignedto_rel ppar JOIN res_users users ON users.id=ppar.res_users_id JOIN res_partner partner ON partner.id=users.partner_id GROUP BY ppar.prisme_postit_id) AS subquery Where prisme_postit.id=subquery.prisme_postit_id; RETURN NEW; END; $$ LANGUAGE plpgsql;""")
        self.env.cr.execute("""CREATE TRIGGER postit_update AFTER INSERT OR UPDATE OR DELETE ON prisme_postit_assignedto_rel WHEN (pg_trigger_depth() < 1) EXECUTE PROCEDURE postit_update();""")
    @api.model
    def action_start(self):
        return self.write({'state': 'get_started'})
    @api.model
    def action_in_process(self):
        return self.write({'state': 'in_process'})
    @api.model
    def action_close(self):
        return self.write({'state': 'terminated'})
    @api.model
    def action_active(self):
        return self.write( {'state': 'active'})

    @api.model
    def scheduled_action(self,context=None):
        #cr, uid, context = self.env.args
        import time
        print 'Lancement du planificateur (' + time.strftime('%d.%m.%Y %H:%M:%S', time.localtime()) + ')'
        self._check_postit_dates()

    @api.model
    def _check_postit_dates(self):
        print 'Scan des postit de la base '
        print self

        #postits_ids = self.search([("state", "!=", "closed")])
        
        postits = self.search([('state', '!=', 'closed')])
        for p in postits:

            print '-------------------------------------------------------'
            print 'Postit en traitement'
            if p.state != "closed":
                print 'Satut ouvert'
                if p.recall_date:
                    recall_date = datetime.strptime(p.recall_date, "%Y-%m-%d")

                    # Si la date de rappelle est passee
                    if  recall_date <= datetime.now():
                        print 'Date de rappel depasse'
                        # Si la garantie est en cours de renouvellement
                        if p.state == "start" or\
                            p.state == "in_process" or\
                            p.state == "active":
                            #self._log('Garantie en cours de renouvellement')
                            # On envoie un rappel uniquement si on est jeudi
                            if p.days:
                                weekday = p.days
                                for day in weekday:
                                    if datetime.now().weekday() == day.nbr:
                                        p._notify_recall(" en cours, echeance le ")
    @api.model
    def _notify_recall(self,message):
        print 'Creation du mail'
        subject = self._construct_subject(message)
        body = self._construct_body()
               
        ass_by = None
        ass_to_list = None
        copy_to_list = None
        if self.assigned_by:
            ass_by = self.assigned_by.email
        if self.assigned_to:
            ass_to_list = self.assigned_to
        if self.copy_to:
            copy_to_list = self.copy_to
        
        sender = 'Prisme - OpenERP (' + self.env.cr.dbname + \
                 ') <system.openerp@prisme.ch>'
            
        # If the field assigned by has been filled
        if ass_by:
            
            # Sending e-mail to the user
            self._send_email(sender, ass_by, subject, body)
        if ass_to_list:
            for ass_to in ass_to_list:
                if not ass_to.email == ass_by:
                    print 'envoie email ass to'
                    self._send_email(sender, ass_to.email, subject, body)
        if copy_to_list:
            for copy_to in copy_to_list:
                if not copy_to == ass_by and not copy_to.email == ass_to.email:
                    print 'envoie email ass by'
                    self._send_email(sender, copy_to, subject, body)
    @api.model
    def _construct_subject(self,message):
        print 'construction du sujet'
        end_date_string = ""
        if self.date_end:
            end_date_string = "(" + self.date_end + ")"
        subject = "Postit (" + self.name + ")"  +message+ end_date_string
        return subject
    @api.model
    def _construct_body(self):
        print 'construction du corps'
       
        body = "Rappel d'expiration de tache" + "\n"
        body = body + "-------------------------------\n\n"
            
        body = body + "Tache: "+ self.name +"\n"

        if self.assigned_by:
            body = body + "Assigne par: " + self.assigned_by.name + "\n"
        if self.partner_id:
            body = body + "Client: " + self.partner_id.name + "\n"
        if self.date_start:
            body = body + "Date de debut: " + self.date_start + "\n"
        if self.date_end:
            body = body + "Date limite: " + self.date_end + "\n" 
        if self.duration:
            body = body + "Duree: " + self.duration + "\n" 
        if self.recall_date:
            body = body + "Date echeance Prisme: " + self.recall_date + "\n\n" 

        if self.assigned_to:
            for ass_to in self.assigned_to:
                body = body + "Assigne a: " + ass_to.name + "\n"
        if self.copy_to:
            for copy_to in self.copy_to:
                body = body + "Copie a: " + copy_to.name + "\n\n"
        if self.description:
            body = body + "Description: \n" + self.description + "\n\n"

        if self.tags:
            body = body + "Type: "
            for type_name in self.tags:
                body = body +" "+ type_name.name
            body = body + "\n"
        return body
    
    @api.model
    def _send_email(self, sender, recipient, subject, body):
        print 'Tentative envoie du mail'
        tools.email_send(email_from=sender, email_to=[recipient] , \
                         subject=subject, body=body)
    @api.model
    def _log(self, message):
        print message






