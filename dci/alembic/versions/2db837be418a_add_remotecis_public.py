#
# Copyright (C) 2017 Red Hat, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""add_remotecis_public

Revision ID: 2db837be418a
Revises: 491df8d6fb62
Create Date: 2017-07-17 08:49:02.237851

"""

# revision identifiers, used by Alembic.
revision = '2db837be418a'
down_revision = '491df8d6fb62'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('remotecis', sa.Column('public', sa.Boolean, default=False))


def downgrade():
    pass
