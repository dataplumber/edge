--*********************************************************************************************
--**  Product Type Model
--**
--**  The product type model is comprised of the following data models:
--**
--**     Product Type Model
--**
--**        - product_type_dataset_view
--**            - dataset_imagery_view
--**                - dataset_imagery
--**                - dataset
--**
--**        - product_type_resource_view
--**            - product_type
--**            - product_type_resource
--**
--**        - product_type_coverage_view
--**            - product_type
--**            - product_type_coverage
--**
--**        - product_type_generation_view
--**            - product_type
--**            - product_type_generation
--**
--**        - product_type_metadata_view
--**            - product_type
--**            - product_type_metadata
--**
--**        - product_type_policy_view
--**            - product_type
--**            - product_type_policy
--**
--**        - product_type_location_policy_view
--**            - product_type
--**            - product_type_location_policy_view
--**
--**        - product_type_provider_view
--**            - product_type
--**            - provider_view (see create_imagery_provider.sql)
--**                 - provider
--**                 - provider_resource_view
--**                     - provider
--**                     - provider_resource
--**                 - provider_contact_view 
--**                     - provider
--**                     - contact
--**
--**        - product_type_element_view
--**            - product_type_element
--**            - product_type_element_dd_view
--**                - product_type_element
--**                - element_dd
--**
--**        - product_type_datetime_view
--**            - product_type
--**            - product_type_datetime
--**
--**        - product_type_character_view
--**            - product_type
--**            - product_type_character
--**
--**        - product_type_integer_view
--**            - product_type
--**            - product_type_integer
--**
--**        - product_type_real_view
--**            - product_type
--**            - product_type_real
--**
--*********************************************************************************************

-----------------------------------------------------------------------------------------------
-- product_type_dataset_view
-----------------------------------------------------------------------------------------------
DROP VIEW IF EXISTS dataset_imagery_view CASCADE;
CREATE VIEW dataset_imagery_view AS
SELECT

   -- dataset_imagery
   dataset_imagery.pt_id       as product_type_id,

   -- dataset
   string_agg(dataset.id::int8::text,
              ',' order by dataset.id) as dataset_id_list,
   string_agg(dataset.revision::int8::text,
              ',' order by dataset.id) as dataset_revision_list,
   string_agg(dataset.description,
              ',' order by dataset.id) as dataset_description_list,
   string_agg(dataset.long_name,
              ',' order by dataset.id) as dataset_long_name_list,
   string_agg(dataset.short_name,
              ',' order by dataset.id) as dataset_short_name_list,
   string_agg(dataset.metadata_endpoint,
              ',' order by dataset.id) as dataset_metadata_endpoint_list,
   string_agg(dataset.metadata_registry,
              ',' order by dataset.id) as dataset_metadata_registry_list,
   string_agg(dataset.remote_dataset_id,
              ',' order by dataset.id) as dataset_remote_dataset_id_list

FROM dataset_imagery
LEFT JOIN dataset ON dataset.id = dataset_imagery.dataset_id
GROUP BY dataset_imagery.pt_id;
SELECT COUNT(*) AS dataset_imagery_view FROM dataset_imagery_view;
--SELECT * FROM dataset_imagery_view ORDER BY product_type_id LIMIT 5;

DROP VIEW IF EXISTS product_type_dataset_view CASCADE;
CREATE VIEW product_type_dataset_view AS
SELECT

   -- product_type
   product_type.id as product_type_id,

   -- dataset_imagery_view
   dataset_imagery_view.dataset_id_list                as product_type_dataset_id_list, 
   dataset_imagery_view.dataset_revision_list          as product_type_dataset_revision_list, 
   dataset_imagery_view.dataset_description_list       as product_type_dataset_description_list,          
   dataset_imagery_view.dataset_long_name_list         as product_type_dataset_long_name_list,            
   dataset_imagery_view.dataset_short_name_list        as product_type_dataset_short_name_list,           
   dataset_imagery_view.dataset_metadata_endpoint_list as product_type_dataset_metadata_endpoint_list,    
   dataset_imagery_view.dataset_metadata_registry_list as product_type_dataset_metadata_registry_list,    
   dataset_imagery_view.dataset_remote_dataset_id_list as product_type_dataset_remote_dataset_id_list

FROM product_type
LEFT JOIN dataset_imagery_view ON dataset_imagery_view.product_type_id = product_type.id
GROUP BY product_type.id,
         dataset_imagery_view.dataset_id_list,  
         dataset_imagery_view.dataset_revision_list,  
         dataset_imagery_view.dataset_description_list,  
         dataset_imagery_view.dataset_long_name_list,  
         dataset_imagery_view.dataset_short_name_list,  
         dataset_imagery_view.dataset_metadata_endpoint_list,
         dataset_imagery_view.dataset_metadata_registry_list,
         dataset_imagery_view.dataset_remote_dataset_id_list;
SELECT COUNT(*) AS product_type_dataset_view FROM product_type_dataset_view;
--SELECT * FROM product_type_dataset_view ORDER BY product_type_id LIMIT 5;

---------------------------------------------------------------------------
-- product_type_resource_view
---------------------------------------------------------------------------
DROP VIEW IF EXISTS product_type_resource_view CASCADE;
CREATE VIEW product_type_resource_view AS
SELECT
   -- product_type
   product_type.id as product_type_id,

   -- product_type_resource
   string_agg(product_type_resource.version::int8::text,
              ',' order by product_type_resource.id) as product_type_resource_version_list,
   string_agg(product_type_resource.type,        
              ',' order by product_type_resource.id) as product_type_resource_type_list,
   string_agg(product_type_resource.name,        
              ',' order by product_type_resource.id) as product_type_resource_name_list,
   string_agg(product_type_resource.path,        
              ',' order by product_type_resource.id) as product_type_resource_path_list,
   string_agg(product_type_resource.description, 
              ',' order by product_type_resource.id) as product_type_resource_description_list
FROM product_type
LEFT JOIN product_type_resource ON product_type_resource.pt_id = product_type.id
GROUP BY product_type.id;
SELECT COUNT(*) AS product_type_resource_view_count FROM product_type_resource_view;
--SELECT * FROM product_type_resource_view LIMIT 5;

---------------------------------------------------------------------------
-- product_type_coverage_view
---------------------------------------------------------------------------
DROP VIEW IF EXISTS product_type_coverage_view CASCADE;
CREATE VIEW product_type_coverage_view AS 
SELECT 
   -- product_type
   product_type.id as product_type_id,
 
   -- product_type_coverage 
   string_agg(product_type_coverage.version::int8::text,
              ',' order by product_type_coverage.id) as product_type_coverage_version_list,
   string_agg(product_type_coverage.north_latitude::real::text,      
              ',' order by product_type_coverage.id) as product_type_coverage_north_latitude_list,
   string_agg(product_type_coverage.east_longitude::real::text,      
              ',' order by product_type_coverage.id) as product_type_coverage_east_longitude_list,
   string_agg(product_type_coverage.south_latitude::real::text,      
              ',' order by product_type_coverage.id) as product_type_coverage_south_latitude_list,
   string_agg(product_type_coverage.west_longitude::real::text,      
              ',' order by product_type_coverage.id) as product_type_coverage_west_longitude_list,
   string_agg(product_type_coverage.start_time::int8::text,          
              ',' order by product_type_coverage.id) as product_type_coverage_start_time_list,
   string_agg(product_type_coverage.stop_time::int8::text,           
              ',' order by product_type_coverage.id) as product_type_coverage_stop_time_list,
   string_agg(('1970-01-01 00:00:00 GMT'::timestamp + ((product_type_coverage.start_time/1000)::text)::interval)::timestamp::text,
              ',' order by product_type_coverage.id) as product_type_coverage_start_time_string_list,
   string_agg(('1970-01-01 00:00:00 GMT'::timestamp + ((product_type_coverage.stop_time/1000)::text)::interval)::timestamp::text, 
              ',' order by product_type_coverage.id) as product_type_coverage_stop_time_string_list
FROM product_type
LEFT JOIN product_type_coverage ON product_type_coverage.pt_id = product_type.id
GROUP BY product_type.id;
SELECT COUNT(*) AS product_type_coverage_view_count FROM product_type_coverage_view;
--SELECT * FROM product_type_coverage_view LIMIT 5;

---------------------------------------------------------------------------
-- product_type_generation_view
---------------------------------------------------------------------------
DROP VIEW IF EXISTS product_type_generation_view CASCADE;
CREATE VIEW product_type_generation_view AS 
SELECT
   -- product_type
   product_type.id as product_type_id,
 
   -- product_type_generation 
   string_agg(product_type_generation.version::int8::text,      
              ',' order by product_type_generation.id) as product_type_generation_version_list,
   string_agg(product_type_generation.mrf_block_size::int8::text,      
              ',' order by product_type_generation.id) as product_type_generation_mrf_block_size_list,
   string_agg(product_type_generation.output_sizex::int8::text,        
              ',' order by product_type_generation.id) as product_type_generation_output_sizex_list,
   string_agg(product_type_generation.output_sizey::int8::text,        
              ',' order by product_type_generation.id) as product_type_generation_output_sizey_list,
   string_agg(product_type_generation.overview_levels::int8::text,     
              ',' order by product_type_generation.id) as product_type_generation_overview_levels_list,
   string_agg(product_type_generation.overview_resample,               
              ',' order by product_type_generation.id) as product_type_generation_overview_resample_list,
   string_agg(product_type_generation.overview_scale::int8::text,      
              ',' order by product_type_generation.id) as product_type_generation_overview_scale_list,
   string_agg(product_type_generation.reprojection_resample,           
              ',' order by product_type_generation.id) as product_type_generation_reprojection_resample_list,
   string_agg(product_type_generation.resize_resample,                 
              ',' order by product_type_generation.id) as product_type_generation_resize_resample_list,
   string_agg(product_type_generation.vrt_nodata,                      
              ',' order by product_type_generation.id) as product_type_generation_vrt_nodata_list
FROM product_type
LEFT JOIN product_type_generation ON product_type_generation.pt_id = product_type.id
GROUP BY product_type.id;
SELECT COUNT(*) AS product_type_generation_view_count FROM product_type_generation_view;
--SELECT * FROM product_type_generation_view LIMIT 5;

---------------------------------------------------------------------------
-- product_type_metadata_view
---------------------------------------------------------------------------
DROP VIEW IF EXISTS product_type_metadata_view;
CREATE VIEW product_type_metadata_view AS 
SELECT
   -- product_type
   product_type.id as product_type_id,
 
   -- product_type_metadata 
   product_type_metadata.version              as product_type_metadata_version,
   product_type_metadata.asc_desc             as product_type_metadata_asc_desc,
   product_type_metadata.science_parameter    as product_type_metadata_science_parameter,
   product_type_metadata.data_version         as product_type_metadata_data_version,
   product_type_metadata.day_night            as product_type_metadata_day_night,
   product_type_metadata.display_resolution   as product_type_metadata_display_resolution,
   product_type_metadata.instrument           as product_type_metadata_instrument,
   product_type_metadata.native_resolution    as product_type_metadata_native_resolution,
   product_type_metadata.platform             as product_type_metadata_platform,
   product_type_metadata.processing_level     as product_type_metadata_processing_level,
   product_type_metadata.project              as product_type_metadata_project,
   product_type_metadata.source_projection_id as product_type_metadata_source_projection_id,
   product_type_metadata.target_projection_id as product_type_metadata_target_projection_id,
   product_type_metadata.region_coverage      as product_type_metadata_region_coverage
FROM product_type
LEFT JOIN product_type_metadata ON product_type_metadata.pt_id = product_type.id
GROUP BY product_type.id,
         product_type_metadata.version,
         product_type_metadata.asc_desc,
         product_type_metadata.science_parameter,
         product_type_metadata.data_version,
         product_type_metadata.day_night,
         product_type_metadata.display_resolution,
         product_type_metadata.instrument,
         product_type_metadata.native_resolution,
         product_type_metadata.platform,
         product_type_metadata.processing_level,
         product_type_metadata.project,
         product_type_metadata.source_projection_id,
         product_type_metadata.target_projection_id,
         product_type_metadata.region_coverage;

SELECT COUNT(*) AS product_type_metadata_view_count FROM product_type_metadata_view;
--SELECT * FROM product_type_metadata_view LIMIT 5;

---------------------------------------------------------------------------
-- product_type_policy_view
---------------------------------------------------------------------------
DROP VIEW IF EXISTS product_type_policy_view;
CREATE VIEW product_type_policy_view AS
SELECT
   -- product_type
   product_type.id as product_type_id,

   -- product_type_policy
   string_agg(product_type_policy.version::int8::text,
              ',' order by product_type_policy.id) as product_type_policy_version_list,
   string_agg(product_type_policy.access_type,
              ',' order by product_type_policy.id) as product_type_policy_access_type_list,
   string_agg(product_type_policy.access_constraint,
              ',' order by product_type_policy.id) as product_type_policy_access_constraint_list,
   string_agg(product_type_policy.use_constraint,
              ',' order by product_type_policy.id) as product_type_policy_use_constraint_list,
   string_agg(product_type_policy.base_path_append_type,
              ',' order by product_type_policy.id) as product_type_policy_base_path_append_type_list,
   string_agg(product_type_policy.checksum_type,
              ',' order by product_type_policy.id) as product_type_policy_checksum_type_list,
   string_agg(product_type_policy.compress_type,
              ',' order by product_type_policy.id) as product_type_policy_compress_type_list,
   string_agg(product_type_policy.data_class,
              ',' order by product_type_policy.id) as product_type_policy_data_class_list,
   string_agg(product_type_policy.data_format,
              ',' order by product_type_policy.id) as product_type_policy_data_format_list,
   string_agg(product_type_policy.spatial_type,
              ',' order by product_type_policy.id) as product_type_policy_spatial_type_list,
   string_agg(product_type_policy.data_duration::int8::text,
              ',' order by product_type_policy.id) as product_type_policy_data_duration_list,
   string_agg(product_type_policy.data_frequency::int8::text,
              ',' order by product_type_policy.id) as product_type_policy_data_frequency_list,
   string_agg(product_type_policy.data_latency::int8::text,
              ',' order by product_type_policy.id) as product_type_policy_data_latency_list,
   string_agg(product_type_policy.data_volume::int8::text,
              ',' order by product_type_policy.id) as product_type_policy_data_volume_list,
   string_agg(product_type_policy.delivery_rate::int8::text,
              ',' order by product_type_policy.id) as product_type_policy_delivery_rate_list,
   string_agg(product_type_policy.multi_day::int8::text,
              ',' order by product_type_policy.id) as product_type_policy_multi_day_list,
   string_agg(product_type_policy.multi_day_link::boolean::text,
              ',' order by product_type_policy.id) as product_type_policy_multi_day_link_list

FROM product_type
LEFT JOIN product_type_policy ON product_type_policy.pt_id = product_type.id
GROUP BY product_type.id;
SELECT COUNT(*) AS product_type_policy FROM product_type_policy_view;
--SELECT * FROM product_type_policy_view LIMIT 5;

---------------------------------------------------------------------------
-- product_type_location_policy_view
---------------------------------------------------------------------------
DROP VIEW IF EXISTS product_type_location_policy_view;
CREATE VIEW product_type_location_policy_view AS
SELECT
   -- product_type
   product_type.id as product_type_id,

   -- product_type_location_policy
   string_agg(product_type_location_policy.version::int8::text,
              ',' order by product_type_location_policy.id) as product_type_location_policy_version_list,
   string_agg(product_type_location_policy.type,
              ',' order by product_type_location_policy.id) as product_type_location_policy_type_list,
   string_agg(product_type_location_policy.base_path,
              ',' order by product_type_location_policy.id) as product_type_location_policy_access_base_path_list
FROM product_type
LEFT JOIN product_type_location_policy ON product_type_location_policy.pt_id = product_type.id
GROUP BY product_type.id;
SELECT COUNT(*) AS product_type_location_policy FROM product_type_location_policy_view;
--SELECT * FROM product_type_location_policy_view LIMIT 5;

--*********************************************************************************************
-- Product Type Provider Model
--*********************************************************************************************

--------------------------------------------------
-- product_type_provider_view
--------------------------------------------------

DROP VIEW IF EXISTS product_type_provider_view CASCADE;
CREATE VIEW product_type_provider_view AS
SELECT

   -- product_type
   product_type.id as product_type_id,

   -- provider_view
   provider_view.provider_version                     as product_type_provider_version,
   provider_view.provider_long_name                   as product_type_provider_long_name,
   provider_view.provider_short_name                  as product_type_provider_short_name,
   provider_view.provider_type                        as product_type_provider_type,            
   provider_view.provider_resource_version_list       as product_type_provider_resource_version_list,
   provider_view.provider_resource_description_list   as product_type_provider_resource_description_list,
   provider_view.provider_resource_name_list          as product_type_provider_resource_name_list,
   provider_view.provider_resource_path_list          as product_type_provider_resource_path_list,
   provider_view.provider_resource_type_list          as product_type_provider_resource_type_list,
   provider_view.provider_contact_version_list        as product_type_provider_contact_version_list,
   provider_view.provider_contact_role_list           as product_type_provider_contact_role_list,
   provider_view.provider_contact_first_name_list     as product_type_provider_contact_first_name_list,
   provider_view.provider_contact_last_name_list      as product_type_provider_contact_last_name_list,
   provider_view.provider_contact_middle_name_list    as product_type_provider_contact_middle_name_list,
   provider_view.provider_contact_address_list        as product_type_provider_contact_address_list,
   provider_view.provider_contact_notify_type_list    as product_type_provider_contact_notify_type_list,
   provider_view.provider_contact_email_list          as product_type_provider_contact_email_list,
   provider_view.provider_contact_phone_list          as product_type_provider_contact_phone_list,
   provider_view.provider_contact_fax_list            as product_type_provider_contact_fax_list

FROM product_type,
     provider_view
WHERE product_type.provider_id = provider_view.provider_id;
SELECT COUNT(*) AS product_type_provider_view_count FROM product_type_provider_view;
--SELECT * FROM product_type_provider_view LIMIT 5;

--*********************************************************************************************
-- Product Type Elements Model
--*********************************************************************************************

--------------------------------------------------
-- product_type_element_view
--------------------------------------------------
DROP VIEW IF EXISTS product_type_element_dd_view CASCADE;
CREATE VIEW product_type_element_dd_view AS
SELECT

   -- product_type_element
   product_type_element.id,
   product_type_element.pt_id                  as product_type_id,
   product_type_element.version                as product_type_element_version,
   product_type_element.obligation_flag        as product_type_element_obligation_flag,
   product_type_element.scope                  as product_type_element_scope,

   -- element_dd
   string_agg(element_dd.version::int8::text,    ';' order by element_dd.id) as product_type_element_dd_versions,
   string_agg(element_dd.type,                   ';' order by element_dd.id) as product_type_element_dd_types,
   string_agg(element_dd.description,            ';' order by element_dd.id) as product_type_element_dd_descriptions,
   string_agg(element_dd.scope,                  ';' order by element_dd.id) as product_type_element_dd_scopes,
   string_agg(element_dd.long_name,              ';' order by element_dd.id) as product_type_element_dd_long_names,
   string_agg(element_dd.short_name,             ';' order by element_dd.id) as product_type_element_dd_short_names,
   string_agg(element_dd.max_length::int8::text, ';' order by element_dd.id) as product_type_element_dd_max_lengths

FROM product_type_element
LEFT JOIN element_dd ON product_type_element.element_id = element_dd.id
GROUP BY product_type_element.id;
SELECT COUNT(*) AS product_type_element_dd_view_count FROM product_type_element_dd_view;
--SELECT * FROM product_type_element_dd_view LIMIT 5;

DROP VIEW IF EXISTS product_type_element_view CASCADE;
CREATE VIEW product_type_element_view AS
SELECT

   -- product_type
   product_type.id as product_type_id,

   -- product_type_element_dd_view
   string_agg(product_type_element_dd_view.product_type_element_version::int8::text,
              ',' order by product_type_element_dd_view.id) as product_type_element_version_list,
   string_agg(product_type_element_dd_view.product_type_element_obligation_flag::boolean::text,
              ',' order by product_type_element_dd_view.id) as product_type_element_obligation_flag_list,
   string_agg(product_type_element_dd_view.product_type_element_scope,
              ',' order by product_type_element_dd_view.id) as product_type_element_scope_list,
   string_agg(product_type_element_dd_view.product_type_element_dd_versions,                   
              ',' order by product_type_element_dd_view.id) as product_type_element_dd_version_list,
   string_agg(product_type_element_dd_view.product_type_element_dd_types,                   
              ',' order by product_type_element_dd_view.id) as product_type_element_dd_type_list,
   string_agg(product_type_element_dd_view.product_type_element_dd_descriptions,            
              ',' order by product_type_element_dd_view.id) as product_type_element_dd_description_list,
   string_agg(product_type_element_dd_view.product_type_element_dd_scopes,                  
              ',' order by product_type_element_dd_view.id) as product_type_element_dd_scope_list,
   string_agg(product_type_element_dd_view.product_type_element_dd_long_names,              
              ',' order by product_type_element_dd_view.id) as product_type_element_dd_long_name_list,
   string_agg(product_type_element_dd_view.product_type_element_dd_short_names,             
              ',' order by product_type_element_dd_view.id) as product_type_element_dd_short_name_list,
   string_agg(product_type_element_dd_view.product_type_element_dd_max_lengths, 
              ',' order by product_type_element_dd_view.id) as product_type_element_dd_max_length_list

FROM product_type
LEFT JOIN product_type_element_dd_view ON product_type_element_dd_view.product_type_id = product_type.id
GROUP BY product_type.id;
SELECT COUNT(*) AS product_type_element_view_count FROM product_type_element_view;
--SELECT * FROM product_type_element_view LIMIT 5;

--------------------------------------------------
-- product_type_datetime_view
--------------------------------------------------

DROP VIEW IF EXISTS product_type_datetime_view CASCADE;
CREATE VIEW product_type_datetime_view AS
SELECT

   -- product_type
   product_type.id as product_type_id,

   -- product_type_datetime
   string_agg(product_type_datetime.version::int8::text,
              ',' order by product_type_datetime.id) as product_type_datetime_version_list,
   string_agg(product_type_datetime.value_long::int8::text,
              ',' order by product_type_datetime.id) as product_type_datetime_value_list,
   string_agg(('1970-01-01 00:00:00 GMT'::timestamp +
              ((product_type_datetime.value_long/1000)::text)::interval)::timestamp::text,
              ',' order by product_type_datetime.id) as product_type_datetime_value_string_list

FROM product_type
LEFT JOIN product_type_datetime ON product_type_datetime.pt_id = product_type.id
GROUP BY product_type.id;
SELECT COUNT(*) AS product_type_datetime_view_count FROM product_type_datetime_view;
--SELECT * FROM product_type_datetime_view LIMIT 5;

--------------------------------------------------
-- product_type_character_view
--------------------------------------------------
DROP VIEW IF EXISTS product_type_character_view CASCADE;
CREATE VIEW product_type_character_view AS
SELECT

   -- product_type
   product_type.id as product_type_id,

   -- product_type_character
   string_agg(product_type_character.version::int8::text,
              ',' order by product_type_character.id) as product_type_character_version_list,
   string_agg(product_type_character.value,
              ',' order by product_type_character.id) as product_type_character_value_list

FROM product_type
LEFT JOIN product_type_character ON product_type_character.pt_id = product_type.id
GROUP BY product_type.id;
SELECT COUNT(*) AS product_type_character_view_count FROM product_type_character_view;
--SELECT * FROM product_type_character_view LIMIT 5;

--------------------------------------------------
-- product_type_integer_view
--------------------------------------------------
DROP VIEW IF EXISTS product_type_integer_view CASCADE;
CREATE VIEW product_type_integer_view AS
SELECT

   -- product_type
   product_type.id as product_type_id,

   -- product_type_integer
   string_agg(product_type_integer.version::int8::text,
              ',' order by product_type_integer.id) as product_type_integer_version_list,
   string_agg(product_type_integer.units,
              ',' order by product_type_integer.id) as product_type_integer_units_list,
   string_agg(product_type_integer.value::int::text,
              ',' order by product_type_integer.id) as product_type_integer_value_list

FROM product_type
LEFT JOIN product_type_integer ON product_type_integer.pt_id = product_type.id
GROUP BY product_type.id;
SELECT COUNT(*) AS product_type_integer_view_count FROM product_type_integer_view;
--SELECT * FROM product_type_integer_view LIMIT 5;

--------------------------------------------------
-- product_type_real_view
--------------------------------------------------
DROP VIEW IF EXISTS product_type_real_view CASCADE;
CREATE VIEW product_type_real_view AS
SELECT

   -- product_type
   product_type.id as product_type_id,

   -- product_type_real
   string_agg(product_type_real.version::int8::text,
              ',' order by product_type_real.id) as product_type_real_version_list,
   string_agg(product_type_real.units,
              ',' order by product_type_real.id) as product_type_real_units_list,
   string_agg(product_type_real.value::numeric::text,
              ',' order by product_type_real.id) as product_type_real_value_list

FROM product_type
LEFT JOIN product_type_real ON product_type_real.pt_id = product_type.id
GROUP BY product_type.id;
SELECT COUNT(*) AS product_type_real_view_count FROM product_type_real_view;
--SELECT * FROM product_type_real_view LIMIT 5;

-----------------------------------------------------------------------------------------------
-- product_type_view
-----------------------------------------------------------------------------------------------
DROP VIEW IF EXISTS product_type_view CASCADE;
CREATE VIEW product_type_view AS 
SELECT 

   -- product_type
   product_type.id,
   product_type.id           as product_type_id, 
   product_type.version      as product_type_version, 
   product_type.provider_id  as product_type_provider_id, 
   product_type.identifier   as product_type_identifier,
   product_type.title        as product_type_title,
   product_type.description  as product_type_description,
   product_type.purgable     as product_type_purgable,
   product_type.purge_rate   as product_type_purge_rate,
   product_type.last_updated as product_type_last_updated,
   '1970-01-01 00:00:00 GMT'::timestamp + ((product_type.last_updated/1000)::text)::interval 
                             as product_type_last_updated_string,

   -- product_type_dataset_view
   product_type_dataset_id_list,
   product_type_dataset_revision_list,
   product_type_dataset_description_list,
   product_type_dataset_long_name_list,
   product_type_dataset_short_name_list,
   product_type_dataset_metadata_endpoint_list,
   product_type_dataset_metadata_registry_list,
   product_type_dataset_remote_dataset_id_list,

   -- product_type_resource
   product_type_resource_version_list,
   product_type_resource_type_list,
   product_type_resource_name_list,
   product_type_resource_path_list,
   product_type_resource_description_list,

   -- product_type_coverage 
   product_type_coverage_version_list,
   product_type_coverage_east_longitude_list,
   product_type_coverage_west_longitude_list,
   product_type_coverage_north_latitude_list,
   product_type_coverage_south_latitude_list,
   product_type_coverage_stop_time_list,
   product_type_coverage_stop_time_string_list,
   product_type_coverage_start_time_list,
   product_type_coverage_start_time_string_list,

   -- product_type_generation
   product_type_generation_version_list,
   product_type_generation_mrf_block_size_list,
   product_type_generation_output_sizex_list,
   product_type_generation_output_sizey_list,
   product_type_generation_overview_levels_list,
   product_type_generation_overview_resample_list,
   product_type_generation_overview_scale_list,
   product_type_generation_reprojection_resample_list,
   product_type_generation_resize_resample_list,
   product_type_generation_vrt_nodata_list,

   -- product_type_metadata
   product_type_metadata_version,
   product_type_metadata_asc_desc,
   product_type_metadata_science_parameter,
   product_type_metadata_data_version,
   product_type_metadata_day_night,
   product_type_metadata_display_resolution,
   product_type_metadata_instrument,
   product_type_metadata_native_resolution,
   product_type_metadata_platform,
   product_type_metadata_processing_level,
   product_type_metadata_project,
   product_type_metadata_source_projection_id,
   product_type_metadata_target_projection_id,
   product_type_metadata_region_coverage,

   -- product_type_policy
   product_type_policy_version_list,
   product_type_policy_access_type_list,
   product_type_policy_access_constraint_list,
   product_type_policy_use_constraint_list,
   product_type_policy_base_path_append_type_list,
   product_type_policy_checksum_type_list,
   product_type_policy_compress_type_list,
   product_type_policy_data_class_list,
   product_type_policy_data_format_list,
   product_type_policy_spatial_type_list,
   product_type_policy_data_duration_list,
   product_type_policy_data_frequency_list,
   product_type_policy_data_latency_list,
   product_type_policy_data_volume_list,
   product_type_policy_delivery_rate_list,
   product_type_policy_multi_day_list,
   product_type_policy_multi_day_link_list,

   -- product_type_location_policy
   product_type_location_policy_version_list,
   product_type_location_policy_type_list,
   product_type_location_policy_access_base_path_list,

   -- product_type_provider_view
   product_type_provider_version,
   product_type_provider_long_name,
   product_type_provider_short_name,
   product_type_provider_type,
   product_type_provider_resource_version_list,
   product_type_provider_resource_description_list,
   product_type_provider_resource_name_list,
   product_type_provider_resource_path_list,
   product_type_provider_resource_type_list,
   product_type_provider_contact_version_list,
   product_type_provider_contact_role_list,
   product_type_provider_contact_first_name_list,
   product_type_provider_contact_last_name_list,
   product_type_provider_contact_middle_name_list,
   product_type_provider_contact_address_list,
   product_type_provider_contact_notify_type_list,
   product_type_provider_contact_email_list,
   product_type_provider_contact_phone_list,
   product_type_provider_contact_fax_list,

   -- product_type_element_view
   product_type_element_obligation_flag_list,
   product_type_element_scope_list,
   product_type_element_dd_version_list,
   product_type_element_dd_type_list,
   product_type_element_dd_description_list,
   product_type_element_dd_scope_list,
   product_type_element_dd_long_name_list,
   product_type_element_dd_short_name_list,
   product_type_element_dd_max_length_list,

   -- product_type_datetime_view
   product_type_datetime_version_list,
   product_type_datetime_value_list,
   product_type_datetime_value_string_list,

   -- product_type_character_view
   product_type_character_version_list,
   product_type_character_value_list,

   -- product_type_integer_view
   product_type_integer_version_list,
   product_type_integer_value_list,
   product_type_integer_units_list,

   -- product_type_real_view
   product_type_real_version_list,
   product_type_real_value_list,
   product_type_real_units_list

FROM
   product_type,
   product_type_dataset_view,
   product_type_resource_view,
   product_type_coverage_view,
   product_type_generation_view,
   product_type_metadata_view,
   product_type_policy_view,
   product_type_location_policy_view,
   product_type_provider_view,
   product_type_element_view,
   product_type_datetime_view,
   product_type_character_view,
   product_type_integer_view,
   product_type_real_view
WHERE
   product_type.id = product_type_dataset_view.product_type_id AND
   product_type.id = product_type_resource_view.product_type_id AND
   product_type.id = product_type_coverage_view.product_type_id AND
   product_type.id = product_type_generation_view.product_type_id AND
   product_type.id = product_type_metadata_view.product_type_id AND
   product_type.id = product_type_policy_view.product_type_id AND
   product_type.id = product_type_location_policy_view.product_type_id AND
   product_type.id = product_type_provider_view.product_type_id AND
   product_type.id = product_type_element_view.product_type_id AND
   product_type.id = product_type_datetime_view.product_type_id AND
   product_type.id = product_type_character_view.product_type_id AND
   product_type.id = product_type_integer_view.product_type_id AND
   product_type.id = product_type_real_view.product_type_id;
SELECT COUNT(*) AS product_type_view_count FROM product_type_view;
--SELECT * FROM product_type_view LIMIT 5;
