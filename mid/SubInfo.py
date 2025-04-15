from psychopy import gui

class SubInfo:
    def __init__(self, config: dict):
        self.fields = config['subinfo_fields']
        self.lang_map = config.get('subinfo_mapping', {})
        self.subject_data = None

        # --- Enforce subject_id field ---
        if not any(f['name'] == 'subject_id' for f in self.fields):
            print("[SubInfo] WARNING: 'subject_id' field missing in config. Adding default.")
            self.fields.insert(0, {
                'name': 'subject_id',
                'type': 'int',
                'constraints': {'min': 101, 'max': 999, 'digits': 3}
            })
            if 'subject_id' not in self.lang_map:
                self.lang_map['subject_id'] = 'Subject ID (3 digits)'

    def _local(self, key: str):
        return self.lang_map.get(key, key)

    def collect(self) -> dict:
        success = False
        responses = None

        while not success:
            dlg = gui.Dlg(title=self._local("Participant Information"))

            for field in self.fields:
                label = self._local(field['name'])
                if field['type'] == 'choice':
                    choices = [self._local(c) for c in field['choices']]
                    dlg.addField(label, choices=choices)
                else:
                    dlg.addField(label)

            responses = dlg.show()

            if responses is None:
                gui.Dlg().addText(self._local("registration_failed")).show()
                return None

            if self.validate(responses):
                self.subject_data = self._format_output(responses)
                gui.Dlg().addText(self._local("registration_successful")).show()
                return self.subject_data

    def validate(self, responses) -> bool:
        for i, field in enumerate(self.fields):
            val = responses[i]
            if field['type'] == 'int':
                try:
                    val = int(val)
                    min_val = field['constraints'].get('min')
                    max_val = field['constraints'].get('max')
                    digits = field['constraints'].get('digits')

                    if min_val is not None and val < min_val:
                        raise ValueError
                    if max_val is not None and val > max_val:
                        raise ValueError
                    if digits is not None and len(str(val)) != digits:
                        raise ValueError
                except:
                    gui.Dlg().addText(
                        self._local("invalid_input").format(field=self._local(field['name']))
                    ).show()
                    return False
        return True

    def _format_output(self, responses) -> dict:
        result = {}
        for i, field in enumerate(self.fields):
            raw = responses[i]
            if field['type'] == 'choice':
                for original in field['choices']:
                    if self._local(original) == raw:
                        raw = original  # Map localized → English
                        break
            result[field['name']] = str(raw)
        return result

    def get_seed(self):
        return int(self.subject_data['subject_id']) if self.subject_data else None
