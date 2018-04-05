# -*- coding: utf-8 -*-

import pytz
import re
import time
import openerp
import openerp.service.report
import uuid
import collections
import babel.dates
from werkzeug.exceptions import BadRequest
from datetime import datetime, timedelta
from dateutil import parser
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from openerp import api
from openerp import tools, SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _
from openerp.http import request
from operator import itemgetter

import logging


class calendar_event(osv.Model):
    """ Model for Calendar Event """
    _inherit = 'calendar.event'

    def _compute(self, cr, uid, ids, fields, arg, context=None):


        res = {}
        user = self.pool['res.users'].browse(cr, 1, 1, context)
        if not isinstance(fields, list):
            fields = [fields]

        for meeting in self.browse(cr, uid, ids, context=context):
            if not user.tz or not meeting.allday:
                return super(calendar_event, self)._compute(cr, uid, ids, fields, arg, context=context)
            if meeting.allday == True:
                offset = datetime.now(pytz.timezone(user.tz)).strftime('%z')

                hours = int(offset[1:3])
                minutes = int(offset[3:])
                if meeting.start_date and meeting.stop_date:
                    start_datetime = datetime.strptime(meeting.start_date, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(hours=hours, minutes=minutes)
                    stop_datetime = datetime.strptime(meeting.stop_date, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(hours=hours, minutes=minutes)
                    meeting_data = {}
                    res[meeting.id] = meeting_data
                    attendee = self._find_my_attendee(cr, uid, [meeting.id], context)
                    for field in fields:
                        if field == 'is_attendee':
                            meeting_data[field] = bool(attendee)
                        elif field == 'attendee_status':
                            meeting_data[field] = attendee.state if attendee else 'needsAction'
                        elif field == 'display_time':
                            meeting_data[field] = self._get_display_time(cr, uid, meeting.start, meeting.stop,
                                                                         meeting.duration, meeting.allday,
                                                                         context=context)
                        elif field == "display_start":
                            meeting_data[field] = meeting.start_date if meeting.allday else meeting.start_datetime
                        elif field == 'start':
                            meeting_data[field] = start_datetime if meeting.allday else meeting.start_datetime
                        elif field == 'stop':
                            meeting_data[field] = stop_datetime if meeting.allday else meeting.stop_datetime
        return res

    _columns = {
        'start': fields.function(_compute, string='Calculated start', type="datetime", multi='attendee', store=True,
                                 required=True),
        'stop': fields.function(_compute, string='Calculated stop', type="datetime", multi='attendee', store=True,
                                required=True),
    }

    # def get_interval(self, cr, uid, ids, date, interval, tz=None, context=None):
    #     if not tz:
    #         tz = self.pool['res.users'].browse(cr, 1, 1, context).tz
    #     return super(calendar_event, self).get_interval(cr, uid, ids, date, interval, tz=tz, context=context)

    def onchange_dates(self, cr, uid, ids, fromtype, start=False, end=False, checkallday=False, allday=False, context=None):

        """Returns duration and end date based on values passed
        @param ids: List of calendar event's IDs.
        """
        value = {}
        user = self.pool['res.users'].browse(cr, 1, 1, context)
        offset = datetime.now(pytz.timezone(user.tz)).strftime('%z')

        hours = int(offset[1:3])
        minutes = int(offset[3:])
        if checkallday != allday:
            return value

        value['allday'] = checkallday  # Force to be rewrited

        if allday:



            if fromtype == 'start' and start:
                if not isinstance(start, datetime):
                    start = datetime.strptime(start, DEFAULT_SERVER_DATE_FORMAT)
                start = datetime.strftime(start + relativedelta(
                    hours=hours, minutes=minutes), DEFAULT_SERVER_DATETIME_FORMAT)
                value['start'] = start


            if fromtype == 'stop' and end:
                if not isinstance(start, datetime):
                    end = datetime.strptime(end, DEFAULT_SERVER_DATE_FORMAT)
                end = datetime.strftime(end + relativedelta(
                    hours=hours, minutes=minutes), DEFAULT_SERVER_DATETIME_FORMAT)
                value['stop'] = end

        else:
            return super(calendar_event, self).onchange_dates(cr, uid, ids, fromtype, start=start, end=end, checkallday=checkallday, allday=allday, context=context)
        return {'value': value}
