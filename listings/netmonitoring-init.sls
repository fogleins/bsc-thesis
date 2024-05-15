{% set vnstat_config_path = '/etc/vnstat.conf' %}
{% set packages = ['vnstat', 'nload', 'nethogs'] %}

{% for package in packages %}
install_package_{{ package }}:
    pkg.installed:
        - name: {{ package }}
{% endfor %}

{% if 'vnstat' in packages or salt['file.file_exists'](vnstat_config_path) %}
update_vnstat_config:
    file.managed:
        - source: salt://manager_org_1/alertmanager_email{{ vnstat_config_path }}
        - name: {{ vnstat_config_path }}
        - user: root
        - group: root
        - mode: 644

enable_vnstatd:
    service.running:
        {% if grains['os_family'] == 'Suse' or grains['os_family'] == 'RedHat' %}
        - name: vnstatd
        {% else %}
        - name: vnstat
        {% endif %}
        - enable: True
        - watch:
            - file: {{ vnstat_config_path }}
{% endif %}
