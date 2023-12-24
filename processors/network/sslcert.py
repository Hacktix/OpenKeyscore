import warnings
from cryptography.utils import CryptographyDeprecationWarning
warnings.filterwarnings('ignore',  category=CryptographyDeprecationWarning)

from nodes import Email, NodeBase, Website
from processor import ProcessorBase
from cryptography import x509
from cryptography.x509.oid import ExtensionOID, NameOID
from util.domain_util import is_excluded_domain, is_excluded_email_domain
import ssl

class SSLCertProcessor(ProcessorBase):
    consumed_nodetypes = [Website, Email]

    def process(self) -> list[NodeBase]:
        nodes = []
        domain = self._get_domain()
        if is_excluded_domain(domain) or is_excluded_email_domain(domain):
            return []

        try:
            certpem = ssl.get_server_certificate((domain, 443), timeout=3)
            cert = x509.load_pem_x509_certificate(certpem.encode("utf-8"))
            subject = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
            nodes.append(Website(subject))
            alt_names = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME).value.get_values_for_type(x509.DNSName)
            for name in alt_names:
                if "*." in name:
                    continue
                nodes.append(Website(name))
        except:
            pass

        return nodes
    
    def _get_domain(self) -> str:
        match(self.node.__class__.__name__):
            case "Website": return self.node.domain
            case "Email": return self.node.email.split("@")[1]
