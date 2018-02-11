class BaseSpreadsheet(object):
    def share(self, value, perm_type, role, notify=True, email_message=None):
        """Share the spreadsheet with other accounts.
        :param value: user or group e-mail address, domain name
                      or None for 'default' type.
        :param perm_type: the account type.
               Allowed values are: ``user``, ``group``, ``domain``,
               ``anyone``.
        :param role: the primary role for this user.
               Allowed values are: ``owner``, ``writer``, ``reader``.
        :param notify: Whether to send an email to the target user/domain.
        :param email_message: The email to be sent if notify=True

        Example::

            # Give Otto a write permission on this spreadsheet
            sh.share('otto@example.com', perm_type='user', role='writer')

            # Transfer ownership to Otto
            sh.share('otto@example.com', perm_type='user', role='owner')

        """
        self.client.insert_permission(
            self.id,
            value=value,
            perm_type=perm_type,
            role=role,
            notify=notify,
            email_message=email_message
        )


class BaseCell(object):
    def __init__(self, worksheet, element):
        pass

    @property
    def row(self):
        """Row number of the cell."""
        return self._row

    @property
    def col(self):
        """Column number of the cell."""
        return self._col

    def __repr__(self):
        return '<%s R%sC%s %s>' % (self.__class__.__name__,
                                   self.row,
                                   self.col,
                                   repr(self.value))
