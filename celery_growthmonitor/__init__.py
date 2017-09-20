#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
django-celery-growthmonitor, a Django helper to monitor jobs running Celery tasks.
Copyright (C) 2017  Marc BOURQUI

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__license__ = 'GNU GPLv3 <https://www.gnu.org/licenses/gpl-3.0.html>'
__author__ = 'Marc Bourqui <pypi.kemar@bourqui.org>'
__version__ = '0.0.0.dev38'
__version_info__ = tuple([int(num) if num.isdigit() else num for num in __version__.replace('-', '.', 1).split('.')])
__status__ = 'Beta'
