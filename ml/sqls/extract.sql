select
    imp.id,
    hour,
    C1,
    banner_pos,
    site_id,
    site_domain,
    site_category,
    app_id,
    app_domain,
    app_category,
    device_id,
    device_ip,
    device_model,
    device_type,
    device_conn_type,
    C14,
    C15,
    C16,
    C17,
    C18,
    C19,
    C20,
    C21,
    case when click is null then 0 else click end as click
from (
    select
        *
    from
        imp_log
) as imp
left join (
    select
        id,
        click
    from
        click_log
) as click
on
    imp.id = click.id;
