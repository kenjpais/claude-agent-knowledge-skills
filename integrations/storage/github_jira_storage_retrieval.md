CREATE TABLE projects (
    project_id        BIGINT PRIMARY KEY,
    project_key       VARCHAR(20) UNIQUE NOT NULL,
    name              VARCHAR(255) NOT NULL,
    description       TEXT,
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP
);

CREATE TABLE issue_types (
    issue_type_id     SMALLINT PRIMARY KEY,
    name              VARCHAR(50) UNIQUE NOT NULL,  -- Epic, Story, Task
    hierarchy_level   SMALLINT NOT NULL             -- Epic=1, Story=2, Task=3
);

CREATE TABLE issues (
    issue_id          BIGINT PRIMARY KEY,
    project_id        BIGINT NOT NULL,
    issue_type_id     SMALLINT NOT NULL,
    parent_issue_id   BIGINT NULL,  -- self-reference for hierarchy

    key               VARCHAR(50) UNIQUE NOT NULL,  -- e.g., PROJ-123
    summary           VARCHAR(500) NOT NULL,
    description       TEXT,

    status            VARCHAR(50),
    priority          VARCHAR(50),

    assignee_id       BIGINT,
    reporter_id       BIGINT,

    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP,
    due_date          TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (issue_type_id) REFERENCES issue_types(issue_type_id),
    FOREIGN KEY (parent_issue_id) REFERENCES issues(issue_id)
);

Issue Links (for non-hierarchical relationships) (Optional)

CREATE TABLE issue_links (
    link_id           BIGINT PRIMARY KEY,
    source_issue_id   BIGINT NOT NULL,
    target_issue_id   BIGINT NOT NULL,
    link_type         VARCHAR(50), -- blocks, relates_to, duplicates

    FOREIGN KEY (source_issue_id) REFERENCES issues(issue_id),
    FOREIGN KEY (target_issue_id) REFERENCES issues(issue_id)
);
Why This Schema Works Well?
:heavy_check_mark: Easy Joins
Everything flows through issues:

-- Get all tasks under an epic
SELECT t.*
FROM issues epic
JOIN issues story ON story.parent_issue_id = epic.issue_id
JOIN issues task  ON task.parent_issue_id = story.issue_id
JOIN tasks t      ON t.issue_id = task.issue_id
WHERE epic.key = 'PROJ-1';

Basically:
issues → shared fields (summary, status, assignee, etc.)
issue_types → tells you if it’s Epic, Story, Task
Now, extensions:
epics → only Epic-specific fields
stories → only Story-specific fields
tasks → only Task-specific fields
Each extension table has a 1:1 relationship with issues.