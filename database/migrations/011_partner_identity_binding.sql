-- AALA PRESSWAALA — Partner Identity Binding / Object-Level Authorization
-- PostgreSQL / Supabase compatible

alter table if exists partners
    add column if not exists user_id uuid references users(id) on delete set null;

create unique index if not exists ux_partners_user_id
    on partners(user_id) where user_id is not null;
create index if not exists ix_partners_user_id on partners(user_id);

-- Link existing partner records to the matching verified user by mobile number.
update partners p
set user_id = u.id
from users u
where p.user_id is null
  and p.mobile_number = u.mobile_number;

-- Ensure partner users have the partner role.
insert into user_roles(user_id, role_id)
select p.user_id, r.id
from partners p
join roles r on r.code = 'partner'
where p.user_id is not null
on conflict do nothing;
