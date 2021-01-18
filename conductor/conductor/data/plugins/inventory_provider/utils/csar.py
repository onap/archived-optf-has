

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import os
import os.path
import requests
from toscaparser.common.exception import ExceptionCollector
from toscaparser.common.exception import ValidationError
from toscaparser.utils.gettextutils import _
from toscaparser.utils.urlutils import UrlUtils
from toscaparser.utils import yamlparser
import yaml
import zipfile


try:  # Python 2.x
    from BytesIO import BytesIO
except ImportError:  # Python 3.x
    from io import BytesIO

TOSCA_META = 'TOSCA-Metadata/TOSCA.meta'
YAML_LOADER = yamlparser.load_yaml


class CSAR(object):
    def __init__(self, csar_file, model_name, a_file=True):
        self.path = csar_file
        self.a_file = a_file
        self.is_validated = False
        self.csar = None
        self.temp_dir = None
        self.is_tosca_metadata = False
        self.main_template_file_name = None
        self.zfile = None
        self.model_name = model_name

    def validate(self):
        """Validate the provided CSAR file."""
        self.is_validated = True
        # validate that the file or URL exists
        missing_err_msg = (_('"%s" does not exist.') % self.path)
        if self.a_file:
            if not os.path.isfile(self.path):
                ExceptionCollector.appendException(
                    ValidationError(message=missing_err_msg))
                return False
            else:
                self.csar = self.path
        else:  # a URL
            if not UrlUtils.validate_url(self.path):
                ExceptionCollector.appendException(
                    ValidationError(message=missing_err_msg))
                return False
            else:
                response = requests.get(self.path)
                self.csar = BytesIO(response.content)

        # validate that it is a valid zip file
        if not zipfile.is_zipfile(self.csar):
            err_msg = (_('"%s" is not a valid zip file.') % self.path)
            ExceptionCollector.appendException(
                ValidationError(message=err_msg))
            return False

        # validate that it contains the metadata file in the correct location
        self.zfile = zipfile.ZipFile(self.csar, 'r')
        filelist = self.zfile.namelist()
        if TOSCA_META in filelist:
            self.is_tosca_metadata = True
            # validate that 'Entry-Definitions' property exists in TOSCA.meta
            is_validated = self._validate_tosca_meta(filelist)
        else:
            self.is_tosca_metadata = False
            is_validated = self._validate_root_level_yaml(filelist)

        if is_validated:
            # validate that external references and imports in the main
            # template actually exist and are accessible
            main_tpl = self._read_template_yaml(self.main_template_file_name)
            nst_properies_res = self.get_nst_properties(main_tpl)
            print("nst properties", nst_properies_res)
            # self._validate_external_references(main_tpl)
        return nst_properies_res

    def get_main_template(self):
        if not self.is_validated:
            self.validate()
        return self.main_template_file_name

    def get_main_template_yaml(self):
        main_template = self.get_main_template()
        if main_template:
            data = self.zfile.read(main_template)
            invalid_tosca_yaml_err_msg = (_('The file "%(template)s" in the CSAR "%(csar)s" does not '
                                            'contain valid TOSCA YAML content.') %
                                          {'template': main_template, 'csar': self.path})
            try:
                tosca_yaml = yaml.safe_load(data)
                if type(tosca_yaml) is not dict:
                    ExceptionCollector.appendException(
                        ValidationError(message=invalid_tosca_yaml_err_msg))
                return tosca_yaml
            except Exception:
                ExceptionCollector.appendException(
                    ValidationError(message=invalid_tosca_yaml_err_msg))

    def _read_template_yaml(self, template):
        data = self.zfile.read(template)
        invalid_tosca_yaml_err_msg = (_('The file "%(template)s" in the CSAR "%(csar)s" does not '
                                        'contain valid YAML content.') %
                                      {'template': template, 'csar': self.path})
        try:
            tosca_yaml = yaml.safe_load(data)
            if type(tosca_yaml) is not dict:
                ExceptionCollector.appendException(
                    ValidationError(message=invalid_tosca_yaml_err_msg))
                return None
            return tosca_yaml
        except Exception:
            ExceptionCollector.appendException(
                ValidationError(message=invalid_tosca_yaml_err_msg))
            return None

    def _validate_tosca_meta(self, filelist):
        tosca = self._read_template_yaml(TOSCA_META)
        if tosca is None:
            return False

        self.metadata = tosca

        if 'Entry-Definitions' not in self.metadata:
            err_msg = (_('The CSAR "%s" is missing the required metadata '
                         '"Entry-Definitions" in '
                         '"TOSCA-Metadata/TOSCA.meta".')
                       % self.path)
            ExceptionCollector.appendException(
                ValidationError(message=err_msg))
            return False

        # validate that 'Entry-Definitions' metadata value points to an
        # existing file in the CSAR
        entry = self.metadata.get('Entry-Definitions')
        if entry and entry not in filelist:
            err_msg = (_('The "Entry-Definitions" file defined in the '
                         'CSAR "%s" does not exist.') % self.path)
            ExceptionCollector.appendException(
                ValidationError(message=err_msg))
            return False

        self.main_template_file_name = entry
        return True

    def _validate_root_level_yaml(self, filelist):
        root_files = []
        for file in filelist:
            if '/' not in file:
                __, file_extension = os.path.splitext(file)
                if file_extension in ['.yaml', '.yml']:
                    root_files.append(file)

        if not len(root_files) == 1:
            err_msg = (_('CSAR file should contain only one root level yaml'
                         ' file. Found "%d" yaml file(s).') % len(root_files))
            ExceptionCollector.appendException(
                ValidationError(message=err_msg))
            return False

        template_data = self._read_template_yaml(root_files[0])
        if template_data is None:
            return False

        tosca_version = template_data.get('tosca_definitions_version')
        if tosca_version == 'tosca_simple_yaml_1_0':
            err_msg = (_('"%s" is not a valid CSAR as it does not contain'
                         ' the required file "TOSCA.meta" in the'
                         ' folder "TOSCA-Metadata".') % self.path)
            ExceptionCollector.appendException(
                ValidationError(message=err_msg))
            return False

        self.metadata = template_data.get('metadata')
        self.main_template_file_name = root_files[0]
        return True

    def get_nst_properties(self, main_tpl):
        importsarr = main_tpl.get('imports')
        for imports in importsarr:
            for key in imports:
                if "service-{}-interface".format(self.model_name) in key:
                    val = imports[key]
        filename = val.get("file")
        datanew = self._read_template_yaml("Definitions/" + filename)
        node_types = datanew.get("node_types")
        for key in list(node_types):
            if "org.openecomp" in key:
                nodedata = node_types[key]
        nst_properties = nodedata.get("properties")
        return nst_properties
