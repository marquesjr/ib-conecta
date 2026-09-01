resource "oci_core_instance" "app" {
  availability_domain = local.availability_domain
  compartment_id      = var.compartment_ocid
  display_name        = var.instance_display_name
  shape               = var.instance_shape

  shape_config {
    ocpus         = var.instance_ocpus
    memory_in_gbs = var.instance_memory_gbs
  }

  source_details {
    source_type = "image"
    source_id   = local.image_id

    boot_volume_size_in_gbs = var.boot_volume_size_gbs
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.public.id
    assign_public_ip = false
    display_name     = "${local.name_prefix}-vnic"
    hostname_label   = "ibconecta"
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
  }

  freeform_tags = local.common_tags
}

data "oci_core_vnic_attachments" "app" {
  compartment_id = var.compartment_ocid
  instance_id    = oci_core_instance.app.id
}

data "oci_core_vnic" "app" {
  vnic_id = data.oci_core_vnic_attachments.app.vnic_attachments[0].vnic_id
}

data "oci_core_private_ips" "app" {
  vnic_id = data.oci_core_vnic.app.id
}

resource "oci_core_public_ip" "app" {
  compartment_id = var.compartment_ocid
  display_name   = "${local.name_prefix}-public-ip"
  lifetime       = "RESERVED"
  private_ip_id  = data.oci_core_private_ips.app.private_ips[0].id

  freeform_tags = local.common_tags
}
