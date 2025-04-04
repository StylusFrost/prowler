from dataclasses import dataclass
from typing import List, Optional

from azure.mgmt.sql import SqlManagementClient

from prowler.lib.logger import logger
from prowler.providers.azure.azure_provider import AzureProvider
from prowler.providers.azure.lib.service.service import AzureService


class SQLServer(AzureService):
    def __init__(self, provider: AzureProvider):
        super().__init__(SqlManagementClient, provider)
        self.sql_servers = self._get_sql_servers()

    def _get_sql_servers(self):
        logger.info("SQL Server - Getting SQL servers...")
        sql_servers = {}
        for subscription, client in self.clients.items():
            try:
                sql_servers.update({subscription: []})
                sql_servers_list = client.servers.list()
                for sql_server in sql_servers_list:
                    resource_group = self._get_resource_group(sql_server.id)
                    auditing_policies = self._get_server_blob_auditing_policies(
                        subscription, resource_group, sql_server.name
                    )
                    firewall_rules = self._get_firewall_rules(
                        subscription, resource_group, sql_server.name
                    )
                    encryption_protector = self._get_enctyption_protectors(
                        subscription, resource_group, sql_server.name
                    )
                    vulnerability_assessment = self._get_vulnerability_assesments(
                        subscription, resource_group, sql_server.name
                    )
                    security_alert_policies = self._get_server_security_alert_policies(
                        subscription, resource_group, sql_server.name
                    )
                    location = self._get_location(
                        subscription, resource_group, sql_server.name
                    )

                    sql_servers[subscription].append(
                        Server(
                            id=sql_server.id,
                            name=sql_server.name,
                            public_network_access=sql_server.public_network_access,
                            minimal_tls_version=sql_server.minimal_tls_version,
                            administrators=ServerExternalAdministrator(
                                sid=getattr(
                                    getattr(sql_server, "administrators", None),
                                    "sid",
                                    "",
                                ),
                                administrator_type=getattr(
                                    getattr(sql_server, "administrators", None),
                                    "administrator_type",
                                    "",
                                ),
                            ),
                            auditing_policies=auditing_policies,
                            firewall_rules=firewall_rules,
                            encryption_protector=encryption_protector,
                            databases=self._get_databases(
                                subscription, resource_group, sql_server.name
                            ),
                            vulnerability_assessment=vulnerability_assessment,
                            security_alert_policies=security_alert_policies,
                            location=location,
                        )
                    )
            except Exception as error:
                logger.error(
                    f"Subscription name: {subscription} -- {error.__class__.__name__}[{error.__traceback__.tb_lineno}]: {error}"
                )
        return sql_servers

    def _get_resource_group(self, id):
        resource_group = id.split("/")[4]
        return resource_group

    def _get_transparent_data_encryption(
        self, subscription, resource_group, server_name, database_name
    ):
        client = self.clients[subscription]
        tde_encrypted = client.transparent_data_encryptions.get(
            resource_group_name=resource_group,
            server_name=server_name,
            database_name=database_name,
            transparent_data_encryption_name="current",
        )
        return tde_encrypted

    def _get_enctyption_protectors(self, subscription, resource_group, server_name):
        client = self.clients[subscription]
        encryption_protectors = client.encryption_protectors.get(
            resource_group_name=resource_group,
            server_name=server_name,
            encryption_protector_name="current",
        )

        current_encryption_protector = EncryptionProtector(
            id=encryption_protectors.id,
            name=encryption_protectors.name,
            type=encryption_protectors.type,
            server_key_name=encryption_protectors.server_key_name,
            server_key_type=encryption_protectors.server_key_type,
        )

        return current_encryption_protector

    def _get_databases(self, subscription, resource_group, server_name):
        logger.info("SQL Server - Getting server databases...")
        databases = []
        try:
            client = self.clients[subscription]
            databases_server = client.databases.list_by_server(
                resource_group_name=resource_group,
                server_name=server_name,
            )
            for database in databases_server:
                tde_encrypted = self._get_transparent_data_encryption(
                    subscription, resource_group, server_name, database.name
                )
                databases.append(
                    Database(
                        id=database.id,
                        name=database.name,
                        type=database.type,
                        location=database.location,
                        managed_by=database.managed_by,
                        tde_encryption=TransparentDataEncryption(
                            id=tde_encrypted.id,
                            name=tde_encrypted.name,
                            type=tde_encrypted.type,
                            location=tde_encrypted.location,
                            status=tde_encrypted.status,
                        ),
                    )
                )
        except Exception as error:
            logger.error(
                f"Subscription name: {subscription} -- {error.__class__.__name__}[{error.__traceback__.tb_lineno}]: {error}"
            )
        return databases

    def _get_vulnerability_assesments(self, subscription, resource_group, server_name):
        client = self.clients[subscription]
        vulnerability_assessment = client.server_vulnerability_assessments.get(
            resource_group_name=resource_group,
            server_name=server_name,
            vulnerability_assessment_name="default",
        )
        return ServerVulnerabilityAssessment(
            id=vulnerability_assessment.id,
            name=vulnerability_assessment.name,
            type=vulnerability_assessment.type,
            storage_container_path=vulnerability_assessment.storage_container_path,
            recurring_scans=VulnerabilityAssessmentRecurringScans(
                is_enabled=vulnerability_assessment.recurring_scans.is_enabled,
                emails=vulnerability_assessment.recurring_scans.emails,
                email_subscription_admins=vulnerability_assessment.recurring_scans.email_subscription_admins,
            ),
        )

    def _get_server_blob_auditing_policies(
        self, subscription, resource_group, server_name
    ):
        client = self.clients[subscription]
        auditing_policies = client.server_blob_auditing_policies.list_by_server(
            resource_group_name=resource_group,
            server_name=server_name,
        )
        auditing_policies_objects = []
        for policy in auditing_policies:
            auditing_policies_objects.append(
                ServerBlobAuditingPolicy(
                    id=policy.id,
                    name=policy.name,
                    type=policy.type,
                    state=policy.state,
                    retention_days=policy.retention_days,
                )
            )
        return auditing_policies_objects

    def _get_firewall_rules(self, subscription, resource_group, server_name):
        client = self.clients[subscription]
        firewall_rules = client.firewall_rules.list_by_server(
            resource_group_name=resource_group, server_name=server_name
        )
        firewall_rules_objects = []
        for rule in firewall_rules:
            firewall_rules_objects.append(
                FirewallRule(
                    name=rule.name,
                    start_ip_address=rule.start_ip_address,
                    end_ip_address=rule.end_ip_address,
                )
            )
        return firewall_rules_objects

    def _get_server_security_alert_policies(
        self, subscription, resource_group, server_name
    ):
        client = self.clients[subscription]
        security_alert_policies = client.server_security_alert_policies.get(
            resource_group_name=resource_group,
            server_name=server_name,
            security_alert_policy_name="default",
        )
        return ServerSecurityAlertPolicy(
            id=security_alert_policies.id,
            name=security_alert_policies.name,
            type=security_alert_policies.type,
            state=security_alert_policies.state,
        )

    def _get_location(self, subscription, resouce_group_name, server_name):
        client = self.clients[subscription]
        location = client.servers.get(resouce_group_name, server_name).location

        return location


@dataclass
class TransparentDataEncryption:
    id: str
    name: str
    type: str
    location: str
    status: str


@dataclass
class Database:
    id: str
    name: str
    type: str
    location: str
    managed_by: str
    tde_encryption: TransparentDataEncryption


@dataclass
class ServerExternalAdministrator:
    sid: str
    administrator_type: str


@dataclass
class ServerBlobAuditingPolicy:
    id: str
    name: str
    type: str
    state: str
    retention_days: int


@dataclass
class FirewallRule:
    name: str
    start_ip_address: str
    end_ip_address: str


@dataclass
class EncryptionProtector:
    id: str
    name: str
    type: str
    server_key_name: str
    server_key_type: str


@dataclass
class VulnerabilityAssessmentRecurringScans:
    is_enabled: bool
    emails: List[str]
    email_subscription_admins: bool


@dataclass
class ServerVulnerabilityAssessment:
    id: str
    name: str
    type: str
    storage_container_path: str
    recurring_scans: VulnerabilityAssessmentRecurringScans


@dataclass
class ServerSecurityAlertPolicy:
    id: str
    name: str
    type: str
    state: str


@dataclass
class Server:
    id: str
    name: str
    public_network_access: str
    minimal_tls_version: str
    administrators: ServerExternalAdministrator
    auditing_policies: List[ServerBlobAuditingPolicy]
    firewall_rules: List[FirewallRule]
    location: str
    encryption_protector: Optional[EncryptionProtector] = None
    vulnerability_assessment: Optional[ServerVulnerabilityAssessment] = None
    security_alert_policies: Optional[ServerSecurityAlertPolicy] = None
    databases: list[Database] = None
