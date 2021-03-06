
import logging

# mv details of this here
from ansible_galaxy import exceptions
from ansible_galaxy import download
from ansible_galaxy.fetch import base
from ansible_galaxy.flat_rest_api.api import GalaxyAPI
from ansible_galaxy.models import content_version
from ansible_galaxy.utils.content_name import parse_content_name

log = logging.getLogger(__name__)


def _build_download_url(external_url=None, version=None):
    if external_url and version:
        archive_url = '%s/archive/%s.tar.gz' % (external_url, version)
        return archive_url


class GalaxyUrlFetch(base.BaseFetch):
    fetch_method = 'galaxy_url'

    def __init__(self, content_spec, content_version,
                 galaxy_context, validate_certs=None):
        super(GalaxyUrlFetch, self).__init__()

        # self.galaxy_url = galaxy_url
        self.content_spec = content_spec
        self.content_version = content_version
        self.galaxy_context = galaxy_context

        self.validate_certs = validate_certs
        if validate_certs is None:
            self.validate_certs = True

        log.debug('Validate TLS certificates: %s', self.validate_certs)

        self.remote_resource = content_spec

    def fetch(self):
        api = GalaxyAPI(self.galaxy_context)

        # FIXME - Need to update our API calls once Galaxy has them implemented
        content_username, repo_name, content_name = parse_content_name(self.content_spec)

        log.debug('content_username=%s', content_username)
        log.debug('repo_name=%s', repo_name)
        log.debug('content_name=%s', content_name)

        # TODO: extract parsing of cli content sorta-url thing and add better tests
        repo_name = repo_name or content_name

        # FIXME: exception handling
        repo_data = api.lookup_repo_by_name(content_username, repo_name)

        if not repo_data:
            raise exceptions.GalaxyClientError("- sorry, %s was not found on %s." % (self.content_spec,
                                                                                     api.api_server))

        # FIXME: ?
        # if repo_data.get('role_type') == 'APP#':
            # Container Role
        #    self.display_callback("%s is a Container App role, and should only be installed using Ansible "
        #                          "Container" % content_name, level='warning')

        # FIXME - Need to update our API calls once Galaxy has them implemented
        related = repo_data.get('related', {})

        repo_versions_url = related.get('versions', None)

        log.debug('related=%s', related)

        # FIXME: exception handling
        repo_versions = api.fetch_content_related(repo_versions_url)

        log.debug('repo_versions: %s', repo_versions)

        # related_repo_url = related.get('repository', None)
        # log.debug('related_repo_url: %s', related_repo_url)
        # related_content_url = related.get('content', None)
        # log.debug('related_content_url: %s', related_content_url)

        # content_repo = None
        # if related_content_url:
        #     content_repo = api.fetch_content_related(related_content_url)
        content_repo_versions = [a.get('name') for a in repo_versions if a.get('name', None)]
        log.debug('content_repo_versions: %s', content_repo_versions)

        # log.debug('content_repo: %s', content_repo)
        # FIXME: mv to it's own method
        # FIXME: pass these to fetch() if it really needs it
        _content_version = content_version.get_content_version(repo_data,
                                                               version=self.content_version,
                                                               content_versions=content_repo_versions,
                                                               content_content_name=content_name)

        # FIXME: stop munging state
        # self.content_meta.version = _content_version

        external_url = repo_data.get('external_url', None)
        if not external_url:
            raise exceptions.GalaxyError('no external_url info on the Repository object from %s',
                                         repo_name)

        download_url = _build_download_url(external_url=external_url, version=_content_version)

        log.debug('content_spec=%s', self.content_spec)
        log.debug('download_url=%s', download_url)

        try:
            content_archive_path = download.fetch_url(download_url,
                                                      validate_certs=self.validate_certs)
        except exceptions.GalaxyDownloadError as e:
            log.exception(e)
            self.display_callback("failed to download the file: %s" % str(e))
            return None

        self.local_path = content_archive_path

        log.debug('content_archive_path=%s', content_archive_path)

        return content_archive_path
