update_/etc/prometheus/alertmanager.yml:
    file.managed:
        - name: /etc/prometheus/alertmanager.yml
        - source: salt://manager_org_1/alertmanager_email/etc/prometheus/alertmanager.yml
        - user: root
        - group: root
        - mode: 644
        
prometheus-alertmanager-service:
    service.running:
        - name: prometheus-alertmanager
        # az alertmanager service automatikusan induljon el boot után
        - enable: True
        # a konfigurációs fájl változását követ(*@ő@*)en a service automatikusan induljon újra
        - watch:
            - file: /etc/prometheus/alertmanager.yml
        
