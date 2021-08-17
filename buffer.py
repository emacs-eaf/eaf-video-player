#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2018 Andy Stewart
#
# Author:     Andy Stewart <lazycat.manatee@gmail.com>
# Maintainer: Andy Stewart <lazycat.manatee@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QSizeF, Qt, QUrl, QRectF, QEvent, QTimer
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPainterPath
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt5.QtWidgets import QWidget, QGraphicsScene, QGraphicsView, QVBoxLayout, QHBoxLayout, QPushButton
from core.buffer import Buffer
from core.utils import interactive, get_emacs_var

class AppBuffer(Buffer):
    def __init__(self, buffer_id, url, arguments):
        Buffer.__init__(self, buffer_id, url, arguments, True)

        self.background_color = QColor(0, 0, 0)

        self.add_widget(VideoPlayer())
        self.buffer_widget.play(url)

        self.build_all_methods(self.buffer_widget)

    def all_views_hide(self):
        # Pause video before all views hdie, otherwise will got error "Internal data stream error".
        if self.buffer_widget.media_player.state() == QMediaPlayer.PlayingState:
            self.buffer_widget.media_player.pause()
            self.buffer_widget.video_need_replay = True

    def some_view_show(self):
        if self.buffer_widget.video_need_replay is True:
            self.buffer_widget.media_player.play()

    def save_session_data(self):
        return str(self.buffer_widget.media_player.position())

    def restore_session_data(self, session_data):
        position = int(session_data)
        self.buffer_widget.media_player.setPosition(position)

    def toggle_play(self):
        if self.buffer_widget.media_player.state() == QMediaPlayer.PlayingState:
            self.buffer_widget.media_player.pause()
            self.buffer_widget.video_need_replay = False
        else:
            self.buffer_widget.media_player.play()
            self.buffer_widget.video_need_replay = True

    def destroy_buffer(self):
        self.buffer_widget.media_player.pause()

        super().destroy_buffer()

class VideoPlayer(QWidget):

    def __init__(self, parent=None):
        super(VideoPlayer, self).__init__(parent)

        self.scene = QGraphicsScene(self)
        self.scene.setBackgroundBrush(QBrush(QColor(0, 0, 0, 255)))

        self.graphics_view = QGraphicsView(self.scene)
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphics_view.setFrameStyle(0)
        self.graphics_view.setStyleSheet("QGraphicsView {background: transparent; border: 3px; outline: none;}")

        self.video_item = QGraphicsVideoItem()

        self.panel_height = 120
        self.progress_bar_height = 120
        self.panel_padding_x = 60
        self.panel_padding_y = (self.panel_height - self.progress_bar_height) / 2

        self.control_panel_widget = QWidget()
        self.control_panel_widget.setStyleSheet("background-color: transparent;")
        self.progress_bar_layout = QHBoxLayout(self.control_panel_widget)
        self.progress_bar_layout.setContentsMargins(self.panel_padding_x, self.panel_padding_y, self.panel_padding_x, self.panel_padding_x)

        self.control_panel = ControlPanel()

        self.progress_bar = ProgressBar()
        self.progress_bar.progress_changed.connect(self.update_video_progress)
        self.progress_bar_layout.addWidget(self.progress_bar)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.graphics_view)

        self.scene.addItem(self.video_item)
        self.scene.addItem(self.control_panel)
        self.control_panel_proxy_widget = self.scene.addWidget(self.control_panel_widget)

        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.positionChanged.connect(self.progress_change)
        self.media_player.setVideoOutput(self.video_item)

        self.video_need_replay = False
        self.video_seek_durcation = 10000 # in milliseconds

        QtCore.QTimer().singleShot(2000, self.hide_control_panel)

        self.graphics_view.viewport().installEventFilter(self)

    def update_video_progress(self, percent):
        self.media_player.setPosition(self.media_player.duration() * percent)

    def progress_change(self, position):
        self.progress_bar.update_progress(self.media_player.duration(), position)

    def resizeEvent(self, event):
        self.video_item.setSize(QSizeF(event.size().width(), event.size().height()))

        self.control_panel.update_size(event.size().width(), self.panel_height)
        self.control_panel.setPos(0, event.size().height() - self.panel_height)

        self.control_panel_widget.resize(event.size().width(), self.panel_height)
        self.control_panel_proxy_widget.setPos(0, event.size().height() - self.panel_height)

        self.progress_bar.resize(event.size().width() - self.panel_padding_x * 2, self.progress_bar_height)

        QWidget.resizeEvent(self, event)

    def play(self, url):
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(url)))
        self.media_player.play()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseMove:
            if event.y() > self.height() - self.progress_bar_height:
                self.show_control_panel()
            else:
                self.hide_control_panel()

        return False

    def hide_control_panel(self):
        self.control_panel.hide()
        self.control_panel_proxy_widget.hide()

    def show_control_panel(self):
        self.control_panel.show()
        self.control_panel_proxy_widget.show()

    @interactive
    def play_forward(self):
        video_position = self.media_player.position()
        self.media_player.setPosition(video_position + self.video_seek_durcation)

    @interactive
    def play_backward(self):
        video_position = self.media_player.position()
        self.media_player.setPosition(max(video_position - self.video_seek_durcation, 0))

    @interactive
    def increase_volume(self):
        self.media_player.setVolume(self.media_player.volume() + 10)

    @interactive
    def decrease_volume(self):
        self.media_player.setVolume(self.media_player.volume() - 10)

    @interactive
    def restart(self):
        self.media_player.setPosition(0)

class ControlPanel(QtWidgets.QGraphicsItem):
    def __init__(self, parent=None):
        super(ControlPanel, self).__init__(parent)
        self.height = 0
        self.width = 0
        self.background_color = QColor(0, 0, 0, 255)
        self.setOpacity(0.5)

    def update_size(self, width, height):
        self.width = width
        self.height = height
        self.update()

    def paint(self, painter, option, widget):
        painter.setPen(self.background_color)
        painter.setBrush(self.background_color)
        painter.drawRect(0, 0, self.width, self.height)

class ProgressBar(QWidget):

    progress_changed = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        self.foreground_color = QColor(get_emacs_var("eaf-emacs-theme-foreground-color"))
        self.background_color = QColor(get_emacs_var("eaf-emacs-theme-background-color"))
        self.position = 0
        self.duration = 0
        self.is_press = False
        self.render_height = 10

    def update_progress(self, duration, position):
        self.position = position
        self.duration = duration

        self.update()

    def mousePressEvent(self, event):
        self.is_press = True
        self.progress_changed.emit(event.x() * 1.0 / self.width())

    def mouseReleaseEvent(self, event):
        self.is_press = False

    def mouseMoveEvent(self, event):
        if self.is_press:
            self.progress_changed.emit(event.x() * 1.0 / self.width())

    def paintEvent(self, event):
        painter = QPainter(self)

        render_y = (self.height() - self.render_height) / 2

        painter.setPen(self.background_color)
        painter.setBrush(self.background_color)
        painter.drawRect(0, render_y, self.width(), self.render_height)

        if self.duration > 0:
            painter.setPen(self.foreground_color)
            painter.setBrush(self.foreground_color)
            painter.drawRect(0, render_y, self.width() * self.position / self.duration, self.render_height)
