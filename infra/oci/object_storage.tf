data "oci_objectstorage_namespace" "app" {
  compartment_id = var.compartment_ocid
}

resource "oci_objectstorage_bucket" "app" {
  compartment_id = var.compartment_ocid
  namespace      = data.oci_objectstorage_namespace.app.namespace
  name           = local.bucket_name
  access_type    = "NoPublicAccess"
  versioning     = var.object_storage_versioning

  freeform_tags = local.common_tags
}
