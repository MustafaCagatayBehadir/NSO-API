from jinja2 import Environment, FileSystemLoader


class NsoConfig:

    def __init__(self):
        self.file_loader = FileSystemLoader("./jinja")
        self.env = Environment(loader=self.file_loader, trim_blocks=True, lstrip_blocks=True)

########################################################################################################################
    def create_tenant_config(self, tenant_info_dict={}):
        template = self.env.get_template("tenant.j2")
        output = template.render(dict_item=tenant_info_dict)

        return output

########################################################################################################################
    def create_pa_config(self, pa_info_dict={}):
        template = self.env.get_template("port_pa.j2")
        output = template.render(dict_item=pa_info_dict)

        return output

########################################################################################################################
    def create_vrf_config(self, vrf_info_dict={}):
        template = self.env.get_template("vrf.j2")
        output = template.render(dict_item=vrf_info_dict)

        return output

########################################################################################################################
    def create_prefix_list_config(self, prefix_list_info_dict={}):
        template = self.env.get_template("prefix_list.j2")
        output = template.render(dict_item=prefix_list_info_dict)

        return output

########################################################################################################################
    def create_service_config(self, service_info_dict={}):
        template = self.env.get_template("service_dclan.j2")
        output = template.render(dict_item=service_info_dict)

        return output

########################################################################################################################
    def create_bd_config(self, bd_info_dict={}):
        template = self.env.get_template("bridge_domain.j2")
        output = template.render(dict_item=bd_info_dict)

        return output

########################################################################################################################
    def create_epg_config(self, epg_info_dict={}):
        template = self.env.get_template("endpoint_group.j2")
        output = template.render(dict_item=epg_info_dict)

        return output

########################################################################################################################
    def create_encap_config(self, encap_info_dict={}):
        template = self.env.get_template("encap.j2")
        output = template.render(dict_item=encap_info_dict)

        return output

########################################################################################################################
    def create_tenant_pa_config(self, tenant_pa_info_dict={}):
        template = self.env.get_template("tenant_pa.j2")
        output = template.render(dict_item=tenant_pa_info_dict)

        return output

########################################################################################################################
    def create_l3direct_config(self, l3direct_info_dict={}):
        template = self.env.get_template("l3direct.j2")
        output = template.render(dict_item=l3direct_info_dict)

        return output

########################################################################################################################
    def create_l3direct_static_config(self, l3direct_static_info_dict):
        template = self.env.get_template("l3direct_static.j2")
        output = template.render(dict_item=l3direct_static_info_dict)

        return output

########################################################################################################################
    def create_l3direct_bgp_config(self, l3direct_bgp_info_dict):
        template = self.env.get_template("l3direct_bgp.j2")
        output = template.render(dict_item=l3direct_bgp_info_dict)

        return output

########################################################################################################################
    def create_l2ext_config(self, l3direct_bgp_info_dict):
        template = self.env.get_template("l2ext.j2")
        output = template.render(dict_item=l3direct_bgp_info_dict)

        return output
