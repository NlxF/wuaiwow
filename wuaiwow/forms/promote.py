# -*- coding: utf-8 -*-


class PromoteForm(object):
    def __init__(self, **kwargs):
        self.pk = kwargs.get('pk', '')
        self.value = kwargs.get('value', '')
        self.name = kwargs.get('name', '')

    def validate(self):
        try:
            self.name = self.name[0] if isinstance(self.name, list) else self.name
            self.pk = int(self.pk[0]) if isinstance(self.pk, list) else int(self.pk)
            if self.pk == 1:
                val = int(self.value[0]) if isinstance(self.value, list) else int(self.value)
                self.value = 70 if val > 70 else 1 if val <= 0 else val
                ret_val = True
            elif self.pk == 2:
                ret_val = True
            elif self.pk == 4:
                self.value = int(self.value[0]) if isinstance(self.value, list) else int(self.value)
                ret_val = True
            elif self.pk == 5:
                self.value = int(self.value[0]) if isinstance(self.value, list) else int(self.value)
                ret_val = self.value in [1, 2]
            else:
                ret_val = False
        except Exception, e:
            ret_val = False

        return ret_val

