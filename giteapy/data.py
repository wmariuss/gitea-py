from os import environ
from termcolor import colored
from giteapy.gitea import GiteaApi
from giteapy.validation import ConfigValidation
from giteapy.exceptions import GiteapyGeneralExceptions


class Data(object):
    def __init__(self, file):
        self.file = file
        self.validation = ConfigValidation()
        self.get_config = self.validation._parse_config(self.file)
        self.validate = self.validation.data_validation(self.get_config)
        self.gitea_api = GiteaApi(url=environ.get('GITEA_URL', ''), token=environ.get('GITEA_TOKEN', ''))
        self.gitea_user = environ.get('GITEA_ADMIN_USER', '')

    def process(self):
        if self.validate is True:
            data = self.get_config
            gitea = data['gitea']
            add = gitea.get('add', '')

            if self.gitea_user == '':
                raise GiteapyGeneralExceptions('Could not see GITEA_ADMIN_USER as env variable')

            if add != '':
                permissions = add.get('permissions', '')
                get_teams = add.get('teams', '')
                repos = add.get('repos', '')

                for org in add.get('organizations', ''):
                    if org:
                        if self.gitea_api.get_org(org) is not None:
                            print(colored('=> {} org exists'.format(org), 'cyan'))
                        else:
                            print(colored('=> Creating {} org'.format(org), 'green'))
                            self.gitea_api.create_org(self.gitea_user, org)

                if get_teams != '':
                    for org, teams in get_teams.items():
                        if org:
                            if self.gitea_api.get_org(org) is not None:
                                teams_list = self.gitea_api.list_orgs_teams(org)
                                owners_list = self.gitea_api.list_team_members(org, 'Owners')

                                if self.gitea_user not in owners_list:
                                    print(colored('=> {0} user does not have access to create teams and add users in {1} org. Please add {0} user in Owners team, {1} org'
                                                  .format(self.gitea_user, org), 'yellow'))
                                else:
                                    if len(teams) >= 1:
                                        for t, users in teams.items():
                                            if t not in teams_list:
                                                print(colored('=> Creating {} team in {} org'.format(t, org), 'green'))
                                                self.gitea_api.create_org_team(org, t)
                                            else:
                                                print(colored('=> {} team exists in {} org'.format(t, org), 'cyan'))

                                            if users is not None:
                                                gitea_users_members_list = self.gitea_api.list_team_members(org, t)
                                                for user in users:
                                                    if user not in gitea_users_members_list:
                                                        print(colored('=> Adding {} member in {} team, {} org'.format(user, t, org), 'green'))
                                                        self.gitea_api.add_team_members(org, t, user)
                                                    else:
                                                        print(colored('=> {} user exists in {} team, {} org'.format(user, t, org), 'cyan'))
                            else:
                                print(colored('=> {} org is not exists'.format(org), 'cyan'))

                if permissions != '':
                    repo_access_list = ['repo.code', 'repo.issues', 'repo.ext_issues', 'repo.wiki', 'repo.pulls', 'repo.releases', 'repo.ext_wiki']
                    team_permission_list = ['read', 'write', 'admin']

                    for org, teams in permissions.items():
                        if org:
                            if self.gitea_api.get_org(org) is not None:
                                owners_list = self.gitea_api.list_team_members(org, 'Owners')

                                if self.gitea_user not in owners_list:
                                    print(colored('=> {0} user does not have access to change permissions in {1} org. Please add {0} user in Owners team, {1} org'
                                                  .format(self.gitea_user, org), 'yellow'))
                                else:
                                    if teams is not None:
                                        for team in teams:
                                            perm = teams.get(team, '')
                                            if perm is not None:
                                                team_permission = perm.get('team', '')
                                                repo_permission = perm.get('repo', '')
                                                if team_permission in team_permission_list:
                                                    if team_permission == 'admin':
                                                        print(colored('=> Updating (admin) permissions for {} team, {} org'.format(team, org), 'green'))
                                                        self.gitea_api.update_permissions(org, team, team_permission)
                                                    else:
                                                        if isinstance(repo_permission, list):
                                                            check_list = any(elem in repo_access_list for elem in repo_permission)
                                                            if check_list:
                                                                print(colored('=> Updating (not admin) permissions for {} team, {} org'.format(team, org), 'green'))
                                                                self.gitea_api.update_permissions(org, team, team_permission, units=repo_permission)
                                                            else:
                                                                print(colored('=> Can not update any permissions for {} team, {} org. Allowed permissions list {}'
                                                                              .format(team, org, repo_access_list), 'red'))
                if repos != '':
                    for org, teams in repos.items():
                        org_repos_list = self.gitea_api.get_org_repos(org)
                        if teams is not None:
                            for team, repos in teams.items():
                                repos_list = self.gitea_api.get_team_repos(org, team)
                                if repos is not None:
                                    for repo in repos:
                                        if repo not in repos_list:
                                            if repo in org_repos_list:
                                                if self.gitea_api.add_repos_team(org, team, repo):
                                                    print(colored('=> {} repo added to {} team, {} org'.format(repo, team, org), 'green'))
                                                else:
                                                    print(colored('=> {} repo could not be added to {} team, {} org'.format(repo, team, org), 'red'))
                                            else:
                                                print(colored('=> {} repo does not exist in {} org'.format(repo, org), 'yellow'))
                                        else:
                                            print(colored('=> {} repo exists in {} team, {} org'.format(repo, team, org), 'cyan'))

            remove = gitea.get('remove', '')

            if remove != '':
                remove = gitea['remove']
                get_remove_members = remove.get('members', '')
                get_remove_teams = remove.get('teams', '')
                get_remove_orgs = remove.get('organizations', '')
                get_remove_repos = remove.get('repos', '')

                if get_remove_members != '':
                    for org, teams in get_remove_members.items():
                        if org:
                            if self.gitea_api.get_org(org) is not None:
                                owners_list = self.gitea_api.list_team_members(org, 'Owners')
                                if self.gitea_user in owners_list:
                                    for team, users in teams.items():
                                        if team:
                                            if users is not None:
                                                gitea_users_members_list = self.gitea_api.list_team_members(org, team)

                                                for user in users:
                                                    if user in gitea_users_members_list:
                                                        print(colored('=> Removing {} member from {} team, {} org'.format(user, team, org), 'yellow'))
                                                        self.gitea_api.remove_team_members(org, team, user)
                                                    else:
                                                        print(colored('=> {} user is not exists in {} team, {} org'.format(user, team, org), 'cyan'))
                                else:
                                    print(colored('=> {0} user does not have access to remove users in {1} org. Please add {0} user in Owners team, {1} org'
                                                  .format(self.gitea_user, org), 'yellow'))
                            else:
                                print(colored('=> You want to remove members from team, but {} org does not exist'.format(org), 'cyan'))

                if get_remove_repos != '':
                    for org, teams in get_remove_repos.items():
                        org_repos_list = self.gitea_api.get_org_repos(org)
                        if teams is not None:
                            for team, repos in teams.items():
                                repos_list = self.gitea_api.get_team_repos(org, team)
                                if repos is not None:
                                    for repo in repos:
                                        if repo in repos_list:
                                            remove_repo_team = self.gitea_api.remove_repos_team(org, team, repo)
                                            if remove_repo_team is not None:
                                                self.gitea_api.remove_repos_team(org, team, repo)
                                                print(colored('=> {} repo removed from {} team, {} org'.format(repo, team, org), 'yellow'))
                                            else:
                                                print(colored('=> {} repo can not be deleted from {} team, {} org'.format(repo, team, org), 'red'))
                                        else:
                                            print(colored('=> {} repo does not exists in {} team, {} org'.format(repo, team, org), 'cyan'))

                if get_remove_teams != '':
                    for org, teams in get_remove_teams.items():
                        if org:
                            if self.gitea_api.get_org(org) is not None:
                                owners_list = self.gitea_api.list_team_members(org, 'Owners')
                                teams_list = self.gitea_api.list_orgs_teams(org)

                                if self.gitea_user in owners_list:
                                    if teams is not None and len(teams) >= 1:
                                        for team in teams:
                                            if team in teams_list:
                                                print(colored('=> Removing {} team from {} organization'.format(team, org), 'yellow'))
                                                self.gitea_api.delete_org_team(org, team)
                                            else:
                                                print(colored('=> {} team is not exists in {} org'.format(team, org), 'cyan'))
                                else:
                                    print(colored('=> {0} user does not have access to remove teams in {1} org. Please add {0} user in Owners team, {1} org'
                                                  .format(self.gitea_user, org), 'yellow'))
                            else:
                                print(colored('=> You want to delete team, but {} org does not exist'.format(org), 'cyan'))

                if get_remove_orgs != '':
                    if len(get_remove_orgs) >= 1:
                        for org in get_remove_orgs:
                            if self.gitea_api.get_org(org) is not None:
                                org_members = self.gitea_api.list_org_members(org)
                                teams_list = self.gitea_api.list_orgs_teams(org)

                                if self.gitea_api.get_org(org) is not None:
                                    if (len(org_members) > 0) and (len(teams_list) > 0):
                                        print(colored('=> To delete {} org you must remove teams and members before'.format(org), 'yellow'))
                                    else:
                                        if self.gitea_user in org_members:
                                            if self.gitea_api.delete_org(org) == 'Deleted':
                                                print(colored('=> {} organization deleted'.format(org), 'yellow'))
                                            elif self.gitea_api.delete_org(org) == 'Not found':
                                                print(colored('=> {} organization not found'.format(org), 'yellow'))
                                        else:
                                            print(colored('=> {0} user does not have permission to delete {1} org'
                                                          .format(self.gitea_user, org), 'yellow'))
                                else:
                                    print(colored('=> {} org is not exists'.format(org), 'cyan'))
                            else:
                                print(colored('=> You want to delete {} org, but this does not exist'.format(org), 'cyan'))
