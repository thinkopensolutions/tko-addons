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
        user = self.pool['res.users'].browse(cr, 1, 1, context)
        tz = pytz.timezone(user.tz) if user.tz else pytz.utc
        res = {}
        if not isinstance(fields, list):
            fields = [fields]

        for meeting in self.browse(cr, uid, ids, context=context):
            if meeting.allday == True:

                if meeting.start_date and meeting.stop_date:
                    start_datetime = datetime.strptime(meeting.start_date, DEFAULT_SERVER_DATE_FORMAT)
                    stop_datetime = datetime.strptime(meeting.stop_date, DEFAULT_SERVER_DATE_FORMAT)
                    start_datetime_tz = start_datetime.utcnow().replace(tzinfo=tz)
                    tz_days_diff = start_datetime_tz.utcoffset().days
                    start_date = start_datetime + relativedelta(days = -1*tz_days_diff)
                    stop_date = stop_datetime + relativedelta(days = -1*tz_days_diff)
                    meeting_data = {}
                    res[meeting.id] = meeting_data
                    attendee = self._find_my_attendee(cr, uid, [meeting.id], context)
                    for field in fields:
                        if field == 'is_attendee':
                            meeting_data[field] = bool(attendee)
                        elif field == 'attendee_status':
                            meeting_data[field] = attendee.state if attendee else 'needsAction'
                        elif field == 'display_time':
                            meeting_data[field] = self._get_display_time(cr, uid, meeting.start, meeting.stop, meeting.duration, meeting.allday, context=context)
                        elif field == "display_start":
                            meeting_data[field] = meeting.start_date if meeting.allday else meeting.start_datetime
                        elif field == 'start':
                            meeting_data[field] = start_date if meeting.allday else meeting.start_datetime
                        elif field == 'stop':
                            meeting_data[field] = stop_date if meeting.allday else meeting.stop_datetime
        return res

    _columns = {
        'start': fields.function(_compute, string='Calculated start', type="datetime", multi='attendee', store=True,
                                 required=True),
        'stop': fields.function(_compute, string='Calculated stop', type="datetime", multi='attendee', store=True,
                                required=True),
    }

