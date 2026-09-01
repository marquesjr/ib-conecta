resource "oci_core_vcn" "app" {
  compartment_id = var.compartment_ocid
  cidr_blocks    = [var.vcn_cidr]
  display_name   = "${local.name_prefix}-vcn"
  dns_label      = "ibconecta"

  freeform_tags = local.common_tags
}

resource "oci_core_internet_gateway" "app" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.app.id
  display_name   = "${local.name_prefix}-igw"
  enabled        = true

  freeform_tags = local.common_tags
}

resource "oci_core_route_table" "public" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.app.id
  display_name   = "${local.name_prefix}-public-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.app.id
  }

  freeform_tags = local.common_tags
}

resource "oci_core_security_list" "public" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.app.id
  display_name   = "${local.name_prefix}-public-sl"

  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }

  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"

    tcp_options {
      min = 80
      max = 80
    }
  }

  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"

    tcp_options {
      min = 443
      max = 443
    }
  }

  dynamic "ingress_security_rules" {
    for_each = var.ssh_allowed_cidrs

    content {
      protocol = "6"
      source   = ingress_security_rules.value

      tcp_options {
        min = 22
        max = 22
      }
    }
  }

  freeform_tags = local.common_tags
}

resource "oci_core_subnet" "public" {
  compartment_id             = var.compartment_ocid
  vcn_id                     = oci_core_vcn.app.id
  cidr_block                 = var.public_subnet_cidr
  display_name               = "${local.name_prefix}-public"
  dns_label                  = "public"
  prohibit_public_ip_on_vnic = false
  route_table_id             = oci_core_route_table.public.id
  security_list_ids          = [oci_core_security_list.public.id]

  freeform_tags = local.common_tags
}
