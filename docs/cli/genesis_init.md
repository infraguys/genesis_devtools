
# genesis_init

Platformize the project

## Usage

```console
                                                                                
 Usage: genesis init [OPTIONS]                                                  
                                                                                
```

## Options

* `force`:
    * Type: boolean
    * Default: `false`
    * Usage: `--force`

  Overwrite existing generated files

* `project_dir`:
    * Type: path
    * Default: `.`
    * Usage: `--project-dir`

  Project directory

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                
 Usage: genesis init [OPTIONS]                                                  
                                                                                

Dynamic options (derived from scenario actions):

  --author-email: Author email
  --author-name: Author name
  --ci-cd: CI/CD configuration
  --enable-pgsql: The project uses PostgreSQL
  --gitlab-deploy-mode: GitLab deploy mode
  --gitlab-genesis-installations: List of installations(comma-separated). List of
    Genesis installations (stands) that should be deployed. Each installation should be
    a valid Genesis installation name. For example: `stage,preprod,prod`
  --gitlab-runner-tag: GitLab runner tag
  --gitlab-templates-repo: Name of templates repository. Name of the GitLab templates
    repository. For example: `ci-templates`
  --manifest-constructor: Manifest constructor
  --manifest-constructor-pg: Manifest PostgreSQL constructor
  --manifest-description: Manifest description. **Manifest** is a YAML file that
    specifies the project's dependencies, infrastructure configuration, and other
    settings. Follow the [developer
    guide](https://infraguys.github.io/genesis_core/guides/developer/elements/) for more
    details.
  --pgsql-database-name: PostgreSQL database name
  --pgsql-usage-mode: Use the communal PG cluster or create your own
  --pgsql-username: PostgreSQL username
  --project-name: Project name
  --project-node-install-nginx: Install Nginx. Install Nginx as a dependency for the
    project. This will install Nginx and configure it to be managed by the project.
  --project-node-install-pm2: Install PM2. Install PM2 as a dependency for the project.
    This will install PM2 and configure it to be managed by the project.
  --project-node-install-redis: Install Redis. Install Redis as a dependency for the
    project. This will install Redis and configure it to be managed by the project.
  --project-node-packages: Project packages (comma-separated). List of packages that
    should be managed by the project. Each package should be a valid package name. For
    example: `package1,package2,package3`
  --project-node-user: Project user. User that will be used to run the project services.
  --project-python-package-manager: Python package manager
  --project-systemd-services: Project systemd services (comma-separated). List of
    systemd services that should be managed by the project. Each service should be a
    valid systemd service name. For example: `service1,service2,service3`
  --project-type: Choose project type
  --project-url: Project URL
  --repository: Repository. Choose the repository where the elements will be stored. It
    can be a local or remote repository. The public repository is used by default.

```
