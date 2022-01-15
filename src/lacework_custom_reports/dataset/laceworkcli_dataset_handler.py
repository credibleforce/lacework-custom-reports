from __future__ import print_function

from .dataset_handler import dataset_handler
import json
import subprocess
from datetime import datetime
import pandas as pd
import re
import os

from concurrent.futures import ThreadPoolExecutor

module_path = os.path.abspath(os.path.dirname(__file__))


class laceworkcli_dataset_handler(dataset_handler):
    def laceworkcli_json_command(self,
                                 command,
                                 args,
                                 subaccount="",
                                 profile="",
                                 api_key="",
                                 api_secret="",
                                 api_token="",
                                 organization=""):
        # build command
        commandline = 'lacework {0} {1} {2} {3} {4} {5} {6} {7} --nocolor --noninteractive --json'.format(
            command,
            args,
            subaccount,
            profile,
            api_key,
            api_secret,
            api_token,
            organization)

        self.logger.debug("Running: {0}".format(commandline))
        proc = subprocess.run(commandline, capture_output=True, text=True, shell=True)

        try:
            return json.loads(proc.stdout)
        except Exception as e:
            self.logger.debug("Failed to parse result: {0}".format(e))
            error_lines = proc.stderr.splitlines()
            error_code = 0
            error_message = None

            self.logger.debug("laceworkcli stderr: {0}".format(error_lines[-4:]))
            m = re.match(r'  \[(\d+)\] (.*)', error_lines[-1])
            if m:
                error_code = m.group(1)
                error_message = m.group(2)

        return {
            "error": True,
            "error_code": error_code,
            "error_message": error_message,
            "command": command,
            "args": args,
            "subaccount": subaccount,
            "profile": profile,
            "api_key": api_key,
            "api_secret": api_secret,
            "api_token": api_token,
            "organization": organization
        }

    def enumerate_aws(self, args_arr, command, subaccount, profile, api_key, api_secret, api_token, organization):
        reports = []
        accounts = self.laceworkcli_json_command(
            command,
            "{0} {1}".format(args_arr[0], "list-accounts"),
            subaccount,
            profile,
            api_key,
            api_secret,
            api_token,
            organization)
        self.logger.info("AWS accounts: {0}".format(accounts))
        if accounts:
            for a in accounts['aws_accounts']:
                reports.append(
                    self.laceworkcli_json_command(
                        command,
                        "{0} {1} {2} {3}".format(
                            args_arr[0],
                            args_arr[1],
                            a,
                            " ".join(args_arr[2:])),
                        subaccount,
                        profile,
                        api_key,
                        api_secret,
                        api_token,
                        organization))
        return reports

    def enumerate_gcp(self, args_arr, command, subaccount, profile, api_key, api_secret, api_token, organization):
        reports = []
        org_projects = self.laceworkcli_json_command(
            command,
            "{0} {1}".format(args_arr[0], "list"),
            subaccount,
            profile,
            api_key,
            api_secret,
            api_token,
            organization)
        self.logger.info("GCP org projects: {0}".format(org_projects))
        if org_projects:
            for op in org_projects['gcp_projects']:
                reports.append(self.laceworkcli_json_command(
                    command,
                    "{0} {1} {2} {3} {4}".format(
                        args_arr[0],
                        args_arr[1],
                        op['organization_id'],
                        op['project_id'],
                        " ".join(args_arr[2:])),
                    subaccount,
                    profile,
                    api_key,
                    api_secret,
                    api_token,
                    organization))
        return reports

    def enumerate_azure(self, args_arr, command, subaccount, profile, api_key, api_secret, api_token, organization):
        reports = []
        tennants = self.laceworkcli_json_command(
            command,
            "{0} {1}".format(args_arr[0], "list-tenants"),
            subaccount,
            profile,
            api_key,
            api_secret,
            api_token,
            organization)
        subscriptions = []

        if tennants:
            for t in tennants.get('azure_tenants'):
                subscriptions.append(
                    self.laceworkcli_json_command(
                        command,
                        "{0} {1} {2}".format(args_arr[0], "list-subscriptions", t),
                        subaccount,
                        profile,
                        api_key,
                        api_secret,
                        api_token,
                        organization))
        self.logger.info("Azure subscriptions: {0}".format(subscriptions))

        if subscriptions:
            for s in subscriptions:
                tenant = s['tenant']['id']
                for s in s['subscriptions']:
                    subscription = s['id']
                    reports.append(
                        self.laceworkcli_json_command(
                            command,
                            "{0} {1} {2} {3} {4}".format(
                                args_arr[0],
                                args_arr[1],
                                tenant,
                                subscription,
                                " ".join(args_arr[2:])),
                            subaccount,
                            profile,
                            api_key,
                            api_secret,
                            api_token,
                            organization))
        return reports

    def enumerate_csp(self, args_arr, command, subaccount, profile, api_key, api_secret, api_token, organization):
        # capture an array of csp result
        result = {
            "csp_type": args_arr[0],
            "reports": []
        }

        if args_arr[0] == "aws":
            result['reports'].extend(self.enumerate_aws(
                args_arr,
                command,
                subaccount,
                profile,
                api_key,
                api_secret,
                api_token,
                organization))
        elif args_arr[0] in ["gcp", "google"]:
            result['reports'].extend(self.enumerate_gcp(
                args_arr,
                command,
                subaccount,
                profile,
                api_key,
                api_secret,
                api_token,
                organization))
        elif args_arr[0] in ["azure", "az"]:
            result['reports'].extend(self.enumerate_azure(
                args_arr,
                command,
                subaccount,
                profile,
                api_key,
                api_secret,
                api_token,
                organization))

        return result

    def transform_vulnerabilities(self, vulnerabilities):
        result = []
        if vulnerabilities:
            for v in vulnerabilities:
                cve = v['cve_id']
                for p in v['packages']:
                    package = "{0}:{1}:{2}".format(cve, p['name'], p['namespace'])
                    result.append(package)

        if len(result) == 0:
            result = "None"

        return result

    def vulnerabilities_task(self, result, cve_summary):
        df = pd.json_normalize(result, sep="_")
        cve_summary['machines_count'] += 1
        # enumerate vulnerability array for each machine and summarize
        for vulns in df['vulnerabilities']:
            if vulns:
                cve_summary['machines_affected'].append(df['host_hostname'])
                cve_summary['machines_affected_count'] += 1
                for v in vulns:
                    cve = v['cve_id']
                    for p in v['packages']:
                        if p['vulnerability_status'] in ['Active', 'Reopened']:
                            if cve not in cve_summary['active_cves']:
                                cve_summary['active_cves'].append(cve)
                                cve_summary['active_cve_count'] += 1

                            package = "{0}:{1}:{2}:{3}:{4}".format(
                                cve,
                                p['name'],
                                p['namespace'],
                                p['severity'],
                                p['vulnerability_status']
                            )

                            if package not in cve_summary['active_cve_packages']:
                                cve_summary['active_cve_packages'].append(package)
                                cve_summary['active_cve_package_count'] += 1

        # create a machine row for each cve
        df = df.explode('vulnerabilities').reset_index(drop=True)
        df['cve_id'] = df['vulnerabilities'].apply(
            lambda x: x.get('cve_id', None) if x is not None else None
        )
        df['packages'] = df['vulnerabilities'].apply(
            lambda x: x.get('packages', None) if x is not None else None
        )
        # create a machine, cve row for each pacakge
        df = df.explode('packages').reset_index(drop=True)
        df = df.join(pd.json_normalize(df.packages))

        # remove unnecessary columns
        df.drop(columns=['packages', 'vulnerabilities'], inplace=True)

        return df, cve_summary

    def host_vuln_callback(self, future):
        result = future.result()
        # self.logger.info(result)
        self.completed += 1

        error = result.get('error', False)
        if error:
            self.logger.error("Completed Job with Error: {0}".format(result))
            if future.result().get('error_code') == '500':
                self.logger.info("Resubmitting job for machine: {0}".format(result.get('args').split(' ')[2]))
        else:
            self.logger.info("Job status: {0}/{1} {2}%".format(
                self.completed,
                self.total_machines,
                round(self.completed/self.total_machines*100, 1))
            )

            df, cve_summary = self.vulnerabilities_task(result, self.cve_summary)
            self.dfs.append(df)

    def enumerate_machine_ids(self,
                              machine_ids,
                              args_arr,
                              command,
                              subaccount,
                              profile,
                              api_key,
                              api_secret,
                              api_token,
                              organization):

        futures = []
        self.dfs = []
        self.cve_summary = {
            "machines_count": 0,
            "machines_affected_count": 0,
            "machines_affected": [],
            "active_cves": [],
            "active_cve_count": 0,
            "active_cve_packages": [],
            "active_cve_package_count": 0
        }
        self.total_machines = len(machine_ids['data']['MID'].keys())
        self.completed = 0

        with ThreadPoolExecutor(max_workers=5) as exe:
            futures = []
            for col in machine_ids['data']['MID']:
                future = exe.submit(
                        self.laceworkcli_json_command,
                        command,
                        "{0} {1} {2} {3}".format(
                            args_arr[0],
                            args_arr[1],
                            machine_ids['data']['MID'][col],
                            " ".join(args_arr[2:])),
                        subaccount,
                        profile,
                        api_key,
                        api_secret,
                        api_token,
                        organization)
                future.add_done_callback(lambda f: self.host_vuln_callback(f))
                futures.append(future)

            # for future in as_completed(futures):
            #     result = future.result()
            #     completed += 1
            #     error = result.get('error', False)
            #     if error:
            #         self.logger.error("Completed Job with Error: {0}".format(result))
            #         if future.result().get('error_code') == '500':
            #             self.logger.info("Resubmitting job for machine: {0}".format(result.get('args').split(' ')[2]))
            #     else:
            #         self.logger.info("Job status: {0}/{1} {2}%".format(
            #             completed,
            #             total_machines,
            #             round(completed/total_machines*100, 1))
            #         )

            #         df, cve_summary = self.vulnerabilities_task(result, cve_summary)
            #         dfs.append(df)

        # concat all results into single dataframe
        df = pd.concat(self.dfs, ignore_index=True)

        return df, self.cve_summary

    def load(self):
        # initialize result objects
        json_data = {}
        data_summary = {}
        machine_ids = []
        machine_summary_required = False

        # check for csp enumeration
        enumerate_csp_accounts = self.dataset.get('enumerate_csp_accounts', False)
        enumerate_machine_ids = self.dataset.get('enumerate_machine_ids', None)

        # retrieve machine ids from existing dataset
        if enumerate_machine_ids:
            machine_ids = self.datasets.get(enumerate_machine_ids)

        command = self.dataset.get('command')
        args = self.dataset.get('args')
        args_arr = args.split(" ")

        # process args hack
        subaccount = ("--subaccount={0}".format(
            self.dataset['subaccount']) if 'subaccount' in self.dataset.keys() and self.dataset['subaccount'] else "")
        profile = ("--profile={0}".format(
            self.dataset['profile']) if 'profile' in self.dataset.keys() and self.dataset['profile'] else "")
        api_key = ("--api_key={0}".format(
            self.dataset['api_key']) if 'api_key' in self.dataset.keys() and self.dataset['api_key'] else "")
        api_secret = ("--api_secret={0}".format(
            self.dataset['api_secret']) if 'api_secret' in self.dataset.keys() and self.dataset['api_secret'] else "")
        api_token = ("--api_token={0}".format(
            self.dataset['api_token']) if 'api_token' in self.dataset.keys() and self.dataset['api_token'] else "")
        organization = "--organization" if 'organization' in self.dataset.keys() and self.dataset['organization'] else ""

        # auto enumerate all known aws accounts, gcp orgs projects, azure tenants subscriptions
        if (enumerate_csp_accounts
                and command == "compliance"
                and args_arr[0] in ["aws", "google", "gcp", "azure", "az"]
                and args_arr[1] == "get-report"):

            result = self.enumerate_csp(args_arr, command, subaccount, profile, api_key, api_secret, api_token, organization)
        elif (enumerate_machine_ids
                and command in ['vulnerability', 'vuln']
                and args_arr[0] in ['host']
                and args_arr[1] in ['show-assessment']):

            # if we're enumerating vulnerabilities we need to provide some summary data
            machine_summary_required = True
            result, cve_summary = self.enumerate_machine_ids(
                machine_ids,
                args_arr,
                command,
                subaccount,
                profile,
                api_key,
                api_secret,
                api_token,
                organization)
        else:
            result = self.laceworkcli_json_command(
                command,
                args,
                subaccount,
                profile,
                api_key,
                api_secret,
                api_token,
                organization)

        # pass through a filter for parsing/manipulation if required
        if self.filterClass is not None:
            json_data, data_summary = self.filterClass().filter(result, dataset=self.dataset)
        else:
            # handle dataframe result
            if type(result) == pd.DataFrame:
                json_data = json.loads(result.to_json(date_format='iso'))
                if machine_summary_required:
                    data_summary = {
                        "rows": len(result.index),
                        "cve_summary": cve_summary
                    }
                else:
                    data_summary = {
                        "rows": len(result.index)
                    }
            else:
                json_data = result
                data_summary = {
                    "rows": len(result)
                }

        self.data = {
            "name": self.dataset.get('name'),
            "data": json_data,
            "summary": {
                "report_time": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                "rows": data_summary.get('rows'),
                "data_summary": data_summary
            }
        }
