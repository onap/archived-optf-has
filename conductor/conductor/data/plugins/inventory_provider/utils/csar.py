

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
from toscaparser.prereq.csar import CSAR
from toscaparser.utils.gettextutils import _
from toscaparser.utils.urlutils import UrlUtils
from toscaparser.utils import yamlparser
import zipfile


try:  # Python 2.x
    from BytesIO import BytesIO
except ImportError:  # Python 3.x
    from io import BytesIO

TOSCA_META = 'TOSCA-Metadata/TOSCA.meta'
YAML_LOADER = yamlparser.load_yaml


class SDCCSAR(CSAR):
    def __init__(self, csar_file, model_name, a_file=True):
        super(SDCCSAR, self).__init__(csar_file, a_file=True)
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
            main_tpl = self._read_template_yaml(self.main_template_file_name)
            nst_properies_res = self.get_nst_properties(main_tpl)
            print("nst properties", nst_properies_res)
        return nst_properies_res

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
