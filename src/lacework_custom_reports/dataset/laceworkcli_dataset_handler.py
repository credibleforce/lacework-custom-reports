from __future__ import print_function

from .dataset_handler import dataset_handler
import json
import subprocess
from datetime import datetime
import pandas as pd
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
        command = 'lacework {0} {1} {2} {3} {4} {5} {6} {7} --nocolor --noninteractive --json'.format(
            command,
            args,
            subaccount,
            profile,
            api_key,
            api_secret,
            api_token,
            organization)

        self.logger.info("Running: {0}".format(command))
        proc = subprocess.run(command, capture_output=True, text=True, shell=True)

        try:
            return json.loads(proc.stdout)
        except Exception as e:
            self.logger.error("Failed to parse json: {0}".format(e))
            self.logger.error("Proc stdout: {0}".format(proc.stdout.splitlines()))
            self.logger.error("Proc stderr: {0}".format(proc.stderr.splitlines()[-4:]))
            return None

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

    def vulnerabilities_count_status(self, status, vulnerabilities):
        result = 0
        if vulnerabilities:
            for v in vulnerabilities:
                for k in v.keys():
                    if k == "packages":
                        for p in v[k]:
                            if p['vulnerability_status'] == status:
                                result += 1
        return result

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

        executor_tasks = []
        machine_limit = 0
        with ThreadPoolExecutor(max_workers=5) as exe:
            i = 0
            for col in machine_ids['data']['MID']:
                machine_id = machine_ids.get('data')['MID'][col]
                self.logger.info("Machine ID: {0}".format(machine_id))

                executor_tasks.append(exe.submit(
                    self.laceworkcli_json_command,
                    command,
                    "{0} {1} {2} {3}".format(
                        args_arr[0],
                        args_arr[1],
                        machine_id,
                        " ".join(args_arr[2:])),
                    subaccount,
                    profile,
                    api_key,
                    api_secret,
                    api_token,
                    organization))
                i += 1

                # allow for debug break
                if machine_limit > 0 and i >= machine_limit:
                    break

        dfs = []
        cve_summary = {
            "active_cves": [],
            "active_cve_count": 0,
            "active_cve_packages": [],
            "active_cve_package_count": 0
        }
        for t in executor_tasks:
            result = t.result()
            if result is not None:
                tdf = pd.json_normalize(result, sep="_")
                for vulns in tdf['vulnerabilities']:
                    if vulns:
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

                # simplify the vulnerability output
                tdf['vulnerabilities'] = tdf['vulnerabilities'].apply(
                    lambda x: self.transform_vulnerabilities(x)
                )
                dfs.append(tdf)

        # concat all results into single dataframe
        df = pd.concat(dfs, ignore_index=True)

        return df, cve_summary

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
