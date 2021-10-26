from typing import Optional


def codeblock(
    content: str, max_size: int = 1024, format_name: Optional[str] = 'py'
) -> str:
    if format_name:
        max_size -= 8 + len(format_name)
        md_format = '```{}\n{}\n```'
    else:
        max_size -= 6
        md_format = '```{1}```'

    if len(content) > max_size:
        content = content[: max_size - 1] + '…'

    return md_format.format(format_name, content)


def clean_codeblock(text: str) -> str:
    if text.startswith('```') and '\n' not in text.splitlines()[0]:
        return '\n'.join(text.splitlines()[1:-1])

    return text.strip('`')
