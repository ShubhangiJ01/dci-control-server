# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Red Hat, Inc
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


def test_create_jobs(admin, jobdefinition_id, team_id, remoteci_id):
    job = admin.post('/api/v1/jobs',
                     data={'jobdefinition_id': jobdefinition_id,
                           'team_id': team_id,
                           'remoteci_id': remoteci_id})
    job_id = job.data['job']['id']
    assert job.status_code == 201

    job = admin.get('/api/v1/jobs/%s' % job_id)
    assert job.status_code == 200


def test_get_all_jobs(admin, jobdefinition_id, team_id, remoteci_id):
    job_1 = admin.post('/api/v1/jobs',
                       data={'jobdefinition_id': jobdefinition_id,
                             'team_id': team_id,
                             'remoteci_id': remoteci_id})
    job_1_id = job_1.data['job']['id']

    job_2 = admin.post('/api/v1/jobs',
                       data={'jobdefinition_id': jobdefinition_id,
                             'team_id': team_id,
                             'remoteci_id': remoteci_id})
    job_2_id = job_2.data['job']['id']

    db_all_jobs = admin.get('/api/v1/jobs?sort=created_at').data
    db_all_jobs = db_all_jobs['jobs']
    db_all_jobs_ids = [db_job['id'] for db_job in db_all_jobs]

    assert db_all_jobs_ids == [job_1_id, job_2_id]


def test_get_all_jobs_with_pagination(admin, jobdefinition_id, team_id,
                                      remoteci_id):
    # create 4 jobs and check meta count
    data = {'jobdefinition_id': jobdefinition_id,
            'team_id': team_id,
            'remoteci_id': remoteci_id}
    admin.post('/api/v1/jobs', data=data)
    admin.post('/api/v1/jobs', data=data)
    admin.post('/api/v1/jobs', data=data)
    admin.post('/api/v1/jobs', data=data)

    # check meta count
    jobs = admin.get('/api/v1/jobs').data
    assert jobs['_meta']['count'] == 4

    # verify limit and offset are working well
    jobs = admin.get('/api/v1/jobs?limit=2&offset=0').data
    assert len(jobs['jobs']) == 2

    jobs = admin.get('/api/v1/jobs?limit=2&offset=2').data
    assert len(jobs['jobs']) == 2

    # if offset is out of bound, the api returns an empty list
    jobs = admin.get('/api/v1/jobs?limit=5&offset=300')
    assert jobs.status_code == 200
    assert jobs.data['jobs'] == []


def test_get_all_jobs_with_embed(admin, jobdefinition_id, team_id,
                                 remoteci_id, test_id):
    # create 2 jobs and check meta data count
    data = {'jobdefinition_id': jobdefinition_id,
            'team_id': team_id,
            'remoteci_id': remoteci_id}
    admin.post('/api/v1/jobs', data=data)
    admin.post('/api/v1/jobs', data=data)

    # verify embed with all embedded options
    query_embed = '/api/v1/jobs?embed=team,remoteci,jobdefinition.test,'\
                  'jobdefinition'
    jobs = admin.get(query_embed).data

    for job in jobs['jobs']:
        assert 'team_id' not in job
        assert 'team' in job
        assert job['team']['id'] == team_id
        assert 'jobdefinition_id' not in job
        assert 'jobdefinition' in job
        assert job['jobdefinition']['id'] == jobdefinition_id
        assert job['jobdefinition']['test']['id'] == test_id
        assert 'remoteci_id' not in job
        assert 'remoteci' in job
        assert job['remoteci']['id'] == remoteci_id

    # verify embed with jobdefinition.test nested
    query_embed = '/api/v1/jobs?embed=jobdefinition.test,'\
                  'jobdefinition'
    jobs = admin.get(query_embed).data

    for job in jobs['jobs']:
        assert 'jobdefinition_id' not in job
        assert 'jobdefinition' in job
        assert job['jobdefinition']['id'] == jobdefinition_id
        assert job['jobdefinition']['test']['id'] == test_id


def test_get_all_jobs_with_embed_not_valid(admin):
    jds = admin.get('/api/v1/jobs?embed=mdr')
    assert jds.status_code == 400


def test_get_all_jobs_with_where(admin, jobdefinition_id, team_id,
                                 remoteci_id):
    job = admin.post('/api/v1/jobs',
                     data={'jobdefinition_id': jobdefinition_id,
                           'team_id': team_id,
                           'remoteci_id': remoteci_id})
    job_id = job.data['job']['id']

    db_job = admin.get('/api/v1/jobs?where=id:%s' % job_id).data
    db_job_id = db_job['jobs'][0]['id']
    assert db_job_id == job_id

    db_job = admin.get(
        '/api/v1/jobs?where=team_id:%s' % team_id).data
    db_job_id = db_job['jobs'][0]['id']
    assert db_job_id == job_id


def test_get_all_jobdefinitions_with_sort(admin, jobdefinition_id, team_id,
                                          remoteci_id):
    # create 3 jobs ordered by created time
    data = {'jobdefinition_id': jobdefinition_id,
            'team_id': team_id,
            'remoteci_id': remoteci_id}
    job_1 = admin.post('/api/v1/jobs', data=data).data['job']
    job_2 = admin.post('/api/v1/jobs', data=data).data['job']
    job_3 = admin.post('/api/v1/jobs', data=data).data['job']

    jobs = admin.get('/api/v1/jobs?sort=created_at').data
    assert jobs['jobs'] == [job_1, job_2, job_3]

    # reverse order by created_at
    jobs = admin.get('/api/v1/jobs?sort=-created_at').data
    assert jobs['jobs'] == [job_3, job_2, job_1]


def test_get_job_by_id(admin, jobdefinition_id, team_id, remoteci_id):
    job = admin.post('/api/v1/jobs',
                     data={'jobdefinition_id': jobdefinition_id,
                           'team_id': team_id,
                           'remoteci_id': remoteci_id})
    job_id = job.data['job']['id']

    job = admin.get('/api/v1/jobs/%s' % job_id)
    assert job.status_code == 200

    job = job.data
    assert job['job']['id'] == job_id


def test_get_jobstates_by_job_id(admin, job_id, team_id):
    data = {'status': 'new', 'team_id': team_id, 'job_id': job_id}
    jobstate_1 = admin.post('/api/v1/jobstates', data=data).data['jobstate']
    jobstate_2 = admin.post('/api/v1/jobstates', data=data).data['jobstate']

    jobstates = admin.get('/api/v1/jobs/%s/jobstates' % job_id)
    jobstates = jobstates.data['jobstates']

    assert jobstates[0]['id'] == jobstate_1['id']
    assert jobstates[1]['id'] == jobstate_2['id']


def test_get_job_not_found(admin):
    result = admin.get('/api/v1/jobs/ptdr')
    assert result.status_code == 404


def test_delete_job_by_id(admin, jobdefinition_id, team_id, remoteci_id):

    job = admin.post('/api/v1/jobs',
                     data={'jobdefinition_id': jobdefinition_id,
                           'team_id': team_id,
                           'remoteci_id': remoteci_id})
    job_id = job.data['job']['id']
    job_etag = job.headers.get("ETag")
    assert job.status_code == 201

    job = admin.get('/api/v1/jobs/%s' % job_id)
    assert job.status_code == 200

    deleted_job = admin.delete('/api/v1/jobs/%s' % job_id,
                               headers={'If-match': job_etag})
    assert deleted_job.status_code == 204

    job = admin.get('/api/v1/jobs/%s' % job_id)
    assert job.status_code == 404