from __future__ import print_function

from .filter_handler import filter_handler
import logging
from datetime import datetime, timedelta
import os

module_path = os.path.abspath(os.path.dirname(__file__))

class laceworksdk_host_vuln_filter_handler(filter_handler):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def filter(self,data,datasets=[]):
        # filter/manipulate the resultant data
        results = []
        for d in data:
            severity = list(d.get('summary').get('severity').keys())[0]
            total_fixed = 0
            total_new = 0
            for p in d.get('packages'):
                
                assessment_date = datetime.fromtimestamp(int(d.get('summary').get('last_evaluation_time'))/1000)
                last_updated_time = datetime.strptime(p.get('last_updated_time'),'%a, %d %b %Y %H:%M:%S %z')
                first_seen_time = datetime.strptime(p.get('first_seen_time'),'%a, %d %b %Y %H:%M:%S %z')
                if p.get('status') == 'Fixed':
                    fixed_time = (first_seen_time + timedelta(minutes=int(p.get('time_to_resolve')))).strftime('%Y-%m-%dT%H:%M:%SZ')
                else:
                    fixed_time = None

                results.append({
                    'assessment_date': assessment_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'cve_id': d.get('cve_id'),
                    'name': p.get('name'),
                    'namespace': p.get('namespace'),
                    'fix_available': p.get('fix_available'),
                    'version': p.get('version'),
                    'fixed_version': p.get('fixed_version'),
                    #'host_count': p.get('host_count'),
                    'severity': p.get('severity'),
                    'cve_link': p.get('cve_link'),
                    'cvss_score': p.get('cvss_score'),
                    #'cvss_v3_score': p.get('cvss_v3_score'),
                    #'cvss_v2_score': p.get('cvss_v3_score'),
                    #'description': p.get('description'),
                    'status': p.get('status'),
                    'package_status': p.get('package_status'),
                    'last_updated_time': last_updated_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'first_seen_time': first_seen_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'time_to_resolve': p.get('time_to_resolve'),
                    'fixed_time': fixed_time,
                    #'total_vulnerabilities': d.get('summary').get('total_vulnerabilities'),
                    #'total_exception_vulnerabilities': d.get('summary').get('total_exception_vulnerabilities'),
                    #'exception_fixable': d.get('summary').get('severity').get(severity).get('exception_fixable'),
                    #'exception_vulnerabilities': d.get('summary').get('severity').get(severity).get('exception_vulnerabilities'),
                    #'fixable': d.get('summary').get('severity').get(severity).get('fixable'),
                    #'vulnerabilities': d.get('summary').get('severity').get(severity).get('vulnerabilities'),
                    #'summary_severity': severity
                })

        # transform
        
        return results