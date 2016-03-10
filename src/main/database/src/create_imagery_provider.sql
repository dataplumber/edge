--*********************************************************************************************
--**  Imagery Provider Model 
--**
--**  The imagery provider model is comprised of the following data models:
--**
--**     Imagery Provider Model
--**        - product_contact_view
--**             - provider_view (intermediate view)
--**             - contact_view (intermediate view)
--**
--*********************************************************************************************

--*********************************************************************************************
-- Imagery Provider Model 
--*********************************************************************************************

--------------------------------------------------
-- provider_resource_view
--------------------------------------------------
DROP VIEW IF EXISTS provider_resource_view CASCADE;
CREATE VIEW provider_resource_view AS
SELECT
   
   -- provider
   provider.id         as provider_id,  

   -- provider_resource
   string_agg(provider_resource.version::int8::text, 
              ',' order by provider_resource.id) as provider_resource_version_list,
   string_agg(provider_resource.description, 
              ',' order by provider_resource.id) as provider_resource_description_list,
   string_agg(provider_resource.name,        
              ',' order by provider_resource.id) as provider_resource_name_list,
   string_agg(provider_resource.path,        
              ',' order by provider_resource.id) as provider_resource_path_list,
   string_agg(provider_resource.type,        
              ',' order by provider_resource.id) as provider_resource_type_list

FROM provider 
LEFT JOIN provider_resource ON provider_resource.provider_id = provider.id
GROUP BY provider.id;
SELECT COUNT(*) AS provider_resource_view_count FROM provider_resource_view;
SELECT * FROM provider_resource_view LIMIT 5;

--------------------------------------------------
-- provider_contact_view
--------------------------------------------------
DROP VIEW IF EXISTS provider_contact_view CASCADE;
CREATE VIEW provider_contact_view AS
SELECT

   -- provider
   provider.id as provider_id,

   -- contact
   string_agg(contact.version::int8::text, ',' order by contact.id) as provider_contact_version_list,
   string_agg(contact.role,                ',' order by contact.id) as provider_contact_role_list,
   string_agg(contact.first_name,          ',' order by contact.id) as provider_contact_first_name_list,
   string_agg(contact.last_name,           ',' order by contact.id) as provider_contact_last_name_list,
   string_agg(contact.middle_name,         ',' order by contact.id) as provider_contact_middle_name_list,
   string_agg(contact.address,             ',' order by contact.id) as provider_contact_address_list,
   string_agg(contact.notify_type,         ',' order by contact.id) as provider_contact_notify_type_list,
   string_agg(contact.email,               ',' order by contact.id) as provider_contact_email_list,
   string_agg(contact.phone,               ',' order by contact.id) as provider_contact_phone_list,
   string_agg(contact.fax,                 ',' order by contact.id) as provider_contact_fax_list

FROM provider
LEFT JOIN contact ON contact.provider_id = provider.id
GROUP BY provider.id;
SELECT COUNT(*) AS provider_contact_view_count FROM provider_contact_view;
SELECT * FROM provider_contact_view LIMIT 5;

--------------------------------------------------
-- provider_view
--------------------------------------------------
DROP VIEW IF EXISTS provider_view CASCADE;
CREATE VIEW provider_view AS
SELECT

   -- provider
   provider.id          as provider_id,
   provider.version     as provider_version,
   provider.long_name   as provider_long_name,
   provider.short_name  as provider_short_name,
   provider.type        as provider_type,

   -- provider_resource_view
   provider_resource_version_list,
   provider_resource_description_list,
   provider_resource_name_list,
   provider_resource_path_list,
   provider_resource_type_list,

   -- provider_contact_view
   provider_contact_version_list,
   provider_contact_role_list,
   provider_contact_first_name_list,
   provider_contact_last_name_list,
   provider_contact_middle_name_list,
   provider_contact_address_list,
   provider_contact_notify_type_list,
   provider_contact_email_list,
   provider_contact_phone_list,
   provider_contact_fax_list

FROM provider, 
     provider_resource_view,
     provider_contact_view
WHERE 
     provider.id = provider_resource_view.provider_id AND
     provider.id = provider_contact_view.provider_id;
SELECT COUNT(*) AS provider_view_count FROM provider_view;
SELECT * FROM provider_view LIMIT 5;

--------------------------------------------------
-- contact_provider_view (used for product)
--------------------------------------------------
DROP VIEW IF EXISTS contact_provider_view CASCADE;
CREATE VIEW contact_provider_view AS
SELECT

   -- contact
   contact.provider_id,
   contact.id           as contact_id,
   contact.version      as contact_version,
   contact.role         as contact_role,
   contact.first_name   as contact_first_name,
   contact.last_name    as contact_last_name,
   contact.middle_name  as contact_middle_name,
   contact.address      as contact_address,
   contact.notify_type  as contact_notify_type,
   contact.email        as contact_email,
   contact.phone        as contact_phone,
   contact.fax          as contact_fax,

   -- provider
   provider.type        as provider_type,
   provider.version     as provider_version,
   provider.long_name   as provider_long_name,
   provider.short_name  as provider_short_name,

   -- provider_resource_view
   provider_resource_view.provider_resource_version_list,
   provider_resource_view.provider_resource_description_list,
   provider_resource_view.provider_resource_name_list,
   provider_resource_view.provider_resource_path_list,
   provider_resource_view.provider_resource_type_list
FROM contact,
     provider,
     provider_resource_view
WHERE contact.provider_id = provider.id
AND   contact.provider_id = provider_resource_view.provider_id;
SELECT COUNT(*) AS contact_provider_view_count FROM contact_provider_view;
SELECT * FROM contact_provider_view LIMIT 5;

--------------------------------------------------
-- dataset_provider_view (no provider id in the dataset )
--------------------------------------------------
DROP VIEW IF EXISTS dataset_provider_view CASCADE;
CREATE VIEW dataset_provider_view AS
SELECT

   -- dataset
   dataset.provider_id,
   dataset.id                as dataset_id,
   dataset.version           as dataset_version,
   dataset.long_name         as dataset_long_name,
   dataset.short_name        as dataset_short_name,
   dataset.metadata_endpoint as dataset_metadata_endpoint,
   dataset.metadata_registry as dataset_metadata_registry,
   dataset.remote_dataset_id as dataset_remote_dataset_id,

   -- provider
   provider.version          as provider_version,
   provider.type             as provider_type,
   provider.long_name        as provider_long_name,
   provider.short_name       as provider_short_name,

   -- provider_resource_view
   provider_resource_view.provider_resource_version_list,
   provider_resource_view.provider_resource_description_list,
   provider_resource_view.provider_resource_name_list,
   provider_resource_view.provider_resource_path_list,
   provider_resource_view.provider_resource_type_list

FROM dataset,
     provider,
     provider_resource_view
WHERE dataset.provider_id = provider.id
AND   dataset.provider_id = provider_resource_view.provider_id;
SELECT COUNT(*) AS dataset_provider_view_count FROM dataset_provider_view;
SELECT * FROM dataset_provider_view LIMIT 5;



