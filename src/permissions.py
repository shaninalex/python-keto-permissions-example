from typing import Mapping

import ory_keto_client
from ory_keto_client import (
    CreateRelationshipBody,
    PermissionApi,
    RelationshipApi,
    SubjectSet,
)
from ory_keto_client.rest import ApiException


NAMESPACE_ROLE = "Role"
ROLE_MEMBER = "member"
WILDCARD_OBJECT = "*"

DEFAULT_POLICY: dict[str, dict[str, list[str]]] = {
    "Order": {
        "office": ["create", "read", "patch", "delete"],
        "warehouse": ["read"],
    },
}


class Permissions:
    def __init__(
        self,
        policy: Mapping[str, Mapping[str, list[str]]] = DEFAULT_POLICY,
        read_url: str = "http://localhost:4466",
        write_url: str = "http://localhost:4467",
    ) -> None:
        self._policy: dict[str, dict[str, list[str]]] = {
            ns: {g: list(perms) for g, perms in groups.items()}
            for ns, groups in policy.items()
        }
        self._read_cfg = ory_keto_client.Configuration(host=read_url)
        self._write_cfg = ory_keto_client.Configuration(host=write_url)

    @property
    def policy(self) -> Mapping[str, Mapping[str, list[str]]]:
        return self._policy

    @property
    def groups(self) -> set[str]:
        return {g for groups in self._policy.values() for g in groups}

    def bootstrap(self) -> None:
        """Write all <Resource>:*#<perm>@Role:<group>#member tuples from the policy."""
        for namespace, groups in self._policy.items():
            for group, perms in groups.items():
                for perm in perms:
                    self._create_tuple(
                        namespace=namespace,
                        object_=WILDCARD_OBJECT,
                        relation=perm,
                        subject_set=SubjectSet(
                            namespace=NAMESPACE_ROLE,
                            object=group,
                            relation=ROLE_MEMBER,
                        ),
                    )

    def teardown(self) -> None:
        for namespace, groups in self._policy.items():
            for group, perms in groups.items():
                for perm in perms:
                    self._delete_tuple(
                        namespace=namespace,
                        object_=WILDCARD_OBJECT,
                        relation=perm,
                        subject_set_namespace=NAMESPACE_ROLE,
                        subject_set_object=group,
                        subject_set_relation=ROLE_MEMBER,
                    )

    def assign_user_to_group(self, user_id: str, group: str) -> None:
        self._require_known_group(group)
        self._create_tuple(
            namespace=NAMESPACE_ROLE,
            object_=group,
            relation=ROLE_MEMBER,
            subject_id=user_id,
        )

    def remove_user_from_group(self, user_id: str, group: str) -> None:
        self._require_known_group(group)
        self._delete_tuple(
            namespace=NAMESPACE_ROLE,
            object_=group,
            relation=ROLE_MEMBER,
            subject_id=user_id,
        )

    def check(
        self,
        user_id: str,
        namespace: str,
        permission: str,
        object_id: str = WILDCARD_OBJECT,
    ) -> bool:
        with ory_keto_client.ApiClient(self._read_cfg) as client:
            api = PermissionApi(client)
            result = api.check_permission(
                namespace=namespace,
                object=object_id,
                relation=permission,
                subject_id=user_id,
            )
            return bool(result.allowed)

    def _require_known_group(self, group: str) -> None:
        if group not in self.groups:
            raise ValueError(
                f"unknown group {group!r}; expected one of {sorted(self.groups)}"
            )

    def _create_tuple(
        self,
        *,
        namespace: str,
        object_: str,
        relation: str,
        subject_id: str | None = None,
        subject_set: SubjectSet | None = None,
    ) -> None:
        body = CreateRelationshipBody(
            namespace=namespace,
            object=object_,
            relation=relation,
        )
        if subject_id is not None:
            body.subject_id = subject_id
        else:
            body.subject_set = subject_set
        with ory_keto_client.ApiClient(self._write_cfg) as client:
            try:
                RelationshipApi(client).create_relationship(create_relationship_body=body)
            except ApiException as e:
                if e.status != 409:
                    raise

    def _delete_tuple(
        self,
        *,
        namespace: str,
        object_: str,
        relation: str,
        subject_id: str | None = None,
        subject_set_namespace: str | None = None,
        subject_set_object: str | None = None,
        subject_set_relation: str | None = None,
    ) -> None:
        kwargs: dict = dict(namespace=namespace, object=object_, relation=relation)
        if subject_id is not None:
            kwargs["subject_id"] = subject_id
        else:
            kwargs["subject_set_namespace"] = subject_set_namespace
            kwargs["subject_set_object"] = subject_set_object
            kwargs["subject_set_relation"] = subject_set_relation
        with ory_keto_client.ApiClient(self._write_cfg) as client:
            try:
                RelationshipApi(client).delete_relationships(**kwargs)
            except ApiException as e:
                if e.status != 404:
                    raise
