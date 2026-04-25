// Copyright © 2023 Ory Corp
// SPDX-License-Identifier: Apache-2.0

import { Namespace, SubjectSet, Context } from "@ory/keto-namespace-types"

class User implements Namespace {}

class Role implements Namespace {
  related: {
    member: User[]
  }
}

class Order implements Namespace {
    related: {
        create: (User | SubjectSet<Role, "member">)[],
        patch: (User | SubjectSet<Role, "member">)[],
        delete: (User | SubjectSet<Role, "member">)[],
        read: (User | SubjectSet<Role, "member">)[],
    }
}

class OrderItem implements Namespace {
    related: {
        parent: Order[]
    }
}
