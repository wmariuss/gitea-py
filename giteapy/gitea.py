import requests
import json

from giteapy.exceptions import GiteapyRequestExceptions


class GiteaApi(object):

    api_baseroute = '/api/v1'

    def __init__(self, url, token=None):
        self.token = token
        self.url = url

        self.headers = {
            'Authorization': 'token {}'.format(self.token),
            'Content-Type': 'application/json',
            'accept': 'application/json'
        }

    def _url(self, api_path):
        url = None
        if self.token:
            # url = 'https://{}{}/{}?token={}'.format(self.url, self.api_baseroute, api_path, self.token)
            url = 'https://{}{}/{}'.format(self.url, self.api_baseroute, api_path)
        else:
            raise GiteapyRequestExceptions('Token is missing')
        return url

    def get_version(self):
        api_version = self._url('version')
        version = requests.get(api_version, headers=self.headers)
        return version.text

    def get_users(self):
        users_list = []

        api_users = self._url('users/search')
        api_list_users = requests.get(api_users, headers=self.headers)
        content = json.loads(api_list_users.text)

        for user in content['data']:
            if user['username']:
                users_list.append(user['username'])
        return users_list

    def create_org(self, username, org_name, full_name="", desc=""):
        api_create_org = self._url('admin/users/{}/orgs'.format(username))
        data = {
            'username': '{}'.format(org_name),
            'full_name': '{}'.format(full_name),
            'description': '{}'.format(desc)
        }

        api_request = requests.post(api_create_org, data=json.dumps(data), headers=self.headers)
        if api_request.status_code == 201:
            return 'Created'
        elif api_request.status_code == 403:
            return 'Forbidden error response'
        elif api_request.status_code == 422:
            return 'Error format response related to input validation'
        return

    def list_orgs_teams(self, org_name):
        teams_list = []
        api_list_teams = self._url('orgs/{}/teams'.format(org_name))
        list_teams = requests.get(api_list_teams, headers=self.headers)
        if list_teams.status_code == 200:
            content = json.loads(list_teams.text)
            for team in content:
                if team['name']:
                    teams_list.append(team['name'])
        return teams_list

    def create_org_team(self, org_name, name, desc="", permission=""):
        api_org_team = self._url('orgs/{}/teams'.format(org_name))
        data = {
            'name': '{}'.format(name),
            'description': '{}'.format(desc),
            'permission': '{}'.format(permission)
        }

        req_api_org_team = requests.post(api_org_team, data=json.dumps(data), headers=self.headers)

        if req_api_org_team.status_code == 201:
            return 'Created'
        return 'Exists'

    def _get_id_team(self, org_name, team_name):
        content = None
        api_team = self._url('orgs/{}/teams'.format(org_name))
        req_api_teams = requests.get(api_team, headers=self.headers)
        if req_api_teams:
            content = json.loads(req_api_teams.text)
            for team in content:
                if team_name == team['name']:
                    return team['id']
        return

    def delete_org_team(self, org_name, team_name):
        team_id = self._get_id_team(org_name, team_name)
        if team_id:
            api_team_url = self._url('teams/{}'.format(team_id))
            api_delete_team = requests.delete(api_team_url, headers=self.headers)
            if api_delete_team.status_code == 204:
                return 'Deleted'
        return 'Not found'

    def list_team_members(self, org_name, team_name):
        team_id = self._get_id_team(org_name, team_name)
        members_list = []
        if team_id:
            api_team_url = self._url('teams/{}/members'.format(team_id))
            req_teams_members = requests.get(api_team_url, headers=self.headers)
            if req_teams_members.status_code == 200:
                content = json.loads(req_teams_members.text)
                for member in content:
                    if member['username']:
                        members_list.append(member['username'])
        return members_list

    def add_team_members(self, org_name, team_name, user):
        get_team_id = self._get_id_team(org_name, team_name)

        if user is not None:
            if get_team_id:
                add_team_mem_url = self._url('teams/{}/members/{}'.format(get_team_id, user))
                req_add_team_mem = requests.put(add_team_mem_url, headers=self.headers)

                if req_add_team_mem.status_code == 204:
                    return 'Added'
        return

    def remove_team_members(self, org_name, team_name, user):
        get_team_id = self._get_id_team(org_name, team_name)

        if user is not None:
            if get_team_id:
                remove_team_mem_url = self._url('teams/{}/members/{}'.format(get_team_id, user))
                req_remove_team_mem = requests.delete(remove_team_mem_url, headers=self.headers)

                if req_remove_team_mem.status_code == 204:
                    return 'Deleted'
        return

    def delete_org(self, org_name):
        api_org = self._url('admin/users/{}'.format(org_name))
        req_delete_org = requests.delete(api_org, headers=self.headers)
        if req_delete_org.status_code == 204:
            return 'Deleted'
        elif req_delete_org.status_code == 404:
            return 'Not found'
        return

    def update_permissions(self, org_name, team_name, permission, description=None, units=[]):
        desc = 'Managed by giteapy'

        if description:
            desc = description

        team_id = self._get_id_team(org_name, team_name)
        data = {
            'name': '{}'.format(team_name),
            'description': desc,
            'permission': '{}'.format(permission),
            'units': units
        }

        if team_id:
            team_perm_url = self._url('teams/{}'.format(team_id))
            req_team_perm = requests.patch(team_perm_url, data=json.dumps(data), headers=self.headers)

            if req_team_perm == 200:
                return 'Updated'
        return

    def get_org(self, org_name):
        api_org = self._url('orgs/{}'.format(org_name))
        req_get_org = requests.get(api_org, headers=self.headers)

        if req_get_org.status_code == 200:
            return org_name
        return

    def list_org_members(self, org_name):
        api_org = self._url('orgs/{}/members'.format(org_name))
        req_get_members = requests.get(api_org, headers=self.headers)
        list_members = json.loads(req_get_members.text)
        members_list = []

        if req_get_members.status_code == 200:
            if len(list_members) > 0:
                for member in list_members:
                    members_list.append(member['username'])
        return members_list

    def get_org_repos(self, org_name):
        org_repos = self._url('orgs/{}/repos'.format(org_name))
        req_org_repo = requests.get(org_repos, headers=self.headers)
        repos_list = []

        if req_org_repo.status_code == 200:
            list_repos = json.loads(req_org_repo.text)
            if len(list_repos) > 0:
                for repo in list_repos:
                    repos_list.append(repo['name'])
        return repos_list

    def add_repos_team(self, org, team, repo):
        get_team_id = self._get_id_team(org, team)
        add_repo_url = self._url('teams/{}/repos/{}/{}'.format(get_team_id, org, repo))
        req_add_repo = requests.put(add_repo_url, headers=self.headers)

        if req_add_repo.status_code == 204:
            return 'Added'
        return

    def get_team_repos(self, org, team):
        get_team_id = self._get_id_team(org, team)
        get_team_repos_url = self._url('teams/{}/repos'.format(get_team_id))
        req_team_repos = requests.get(get_team_repos_url, headers=self.headers)
        team_repos_list = json.loads(req_team_repos.text)
        repos_list = []

        if req_team_repos.status_code == 200:
            for repo in team_repos_list:
                repos_list.append(repo['name'])
        return repos_list

    def remove_repos_team(self, org, team, repo):
        get_team_id = self._get_id_team(org, team)
        remove_repo_url = self._url('teams/{}/repos/{}/{}'.format(get_team_id, org, repo))
        req_remove_repos = requests.delete(remove_repo_url, headers=self.headers)

        if req_remove_repos.status_code == 204:
            return 'Deleted'
        return
