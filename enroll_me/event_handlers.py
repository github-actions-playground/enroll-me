"""Webhook event handlers."""
import logging

from gidgethub import InvalidField

from octomachinery.app.routing import process_event_actions
from octomachinery.app.routing.decorators import process_webhook_payload
from octomachinery.app.runtime.context import RUNTIME_CONTEXT
from octomachinery.app.runtime.installation_utils import (
    get_installation_config,
)


logger = logging.getLogger(__name__)


@process_event_actions('issue_comment', {'created'})
@process_webhook_payload
async def on_issue_commented(
        *,
        action, issue, comment, repository=None,
        organization=None, sender=None,
        installation=None,
        assignee=None, changes=None,
):
    """Create a repo for a user who added a comment to an issue."""
    gh_api = RUNTIME_CONTEXT.app_installation_client
    bot_sign = '\n\n--🤖'

    is_pr_comment = 'pull_request' in issue
    issue_title = issue['title']
    comment_author = comment['user']['login']

    if is_pr_comment:
        """Only react to comments to issues, not PRs."""
        logger.info('This is a PR comment, skipping')
        return

    config = await get_installation_config()
    app_config = config.get('enroll-me', {})
    event_config = app_config.get(issue_title, {})
    issue_access_list = event_config.get('users', [])
    issue_repo_slug = event_config.get(
        'slug',
        '-'.join(issue_title.lower().split()),
    )

    # await gh_api.post(
    #     f'comment["url"]/reactions',
    #     preview_api_version='squirrel-girl',
    #     data={'content': 'eyes'},
    # )

    reaction_comment = await gh_api.post(
        issue['comments_url'],
        data={
            'body':
            f'@{comment_author} Beep beep boop! I’m a bot!\n'
            '![](https://cdn-images-1.medium.com/max/1600'
            f'/1*o9B5BFh3haqBHLSfwUf_oA.gif)\nStay tuned!{bot_sign}',
        },
    )
    

    if comment_author not in issue_access_list:
        logger.info(
            '@%s is not listed in the access list for %s, skipping',
            comment_author,
            issue_title,
        )
        await gh_api.patch(
            reaction_comment['url'],
            data={
                'body':
                f'@{comment_author} Oops...\n'
                'You are not on the access list, '
                'I cannot create a repo for you.\n'
                f'Sooooooooorrryyy!{bot_sign}',
            },
        )
        return

    await gh_api.patch(
        reaction_comment['url'],
        data={'body': f'@{comment_author} on it!{bot_sign}'},
    )

    repo_name = f'{issue_repo_slug}-{comment_author}'
    logger.info(
        'Creating %s/%s...',
        organization["repos_url"],
        repo_name,
    )

    try:
        repo = await gh_api.post(
            organization["repos_url"],
            data={'name': repo_name},
        )
        # await gh_api.post(
        #     f'comment["url"]/reactions',
        #     preview_api_version='squirrel-girl',
        #     data={'content': 'hooray'},
        # )
        await gh_api.put(
            f'repo["collaborators_url"]/{comment_author}',
            data={'permission': 'admin'},
        )
    except InvalidField as gh_exc:
        logger.info(
            'Attempt to create %s/%s has failed: %s',
            organization["repos_url"],
            repo_name,
            gh_exc.errors,
        )
        # await gh_api.post(
        #     f'comment["url"]/reactions',
        #     preview_api_version='squirrel-girl',
        #     data={'content': 'confused'},
        # )
        await gh_api.patch(
            reaction_comment['url'],
            data={
                'body':
                f'@{comment_author} Oops...\n'
                'I cannot create a repo for you.'
                'Something went wrong...\n'
                f'Sooooooooorrryyy!{bot_sign}\n\n'
                '<details>\n<summary>More info</summary>\n\n'
                f'{gh_exc.errors}\n</details>',
            },
        )
    else:
        # await gh_api.post(
        #     f'comment["url"]/reactions',
        #     preview_api_version='squirrel-girl',
        #     data={'content': 'rocket'},
        # )
        await gh_api.patch(
            reaction_comment['url'],
            data={
                'body':
                f'@{comment_author} Here\'s your repo: '
                f'{repo["html_url"]}{bot_sign}',
            },
        )
