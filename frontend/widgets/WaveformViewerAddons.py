





        self.captureDataButton = Button("Capture Visible Data", on_click=self.captureVisibleData)
        hlayout.addWidget(self.captureDataButton)


        self.label = pg.TextItem()
        self.label.setZValue(20)
        self.proxy = pg.SignalProxy(self.waveformPlot1.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.waveformPlot1.addItem(self.label)





    @staticmethod
    def eng_format(x, pos=0):
        'The two args are the value and tick position'
        magnitude = 0
        while abs(x) >= 1000:
            magnitude += 1
            x /= 1000.0
        while abs(x) < 1 and magnitude > -3:
            magnitude -= 1
            x *= 1000.0
        # add more suffixes if you need them
        return '{}{}'.format('{:.0f}'.format(x).rstrip('0').rstrip('.'), ['p', 'n', 'u', 'm', '', 'K', 'M', 'G', 'T', 'P'][magnitude+4])
    

    def mouseMoved(self, evt):
        pos = evt[0]  # using signal proxy turns original arguments into a tuple
        if self.waveformPlot1.sceneBoundingRect().contains(pos):
            mousePoint = self.waveformPlot1.vb.mapSceneToView(pos)
            index = int(mousePoint.x())
            if 0 <= index < len(self.x):
                # Set the size of the text
                xstr = self.eng_format(mousePoint.x())
                ystr = self.eng_format(mousePoint.y())
                self.label.setText(f"x={xstr}, y={ystr}")
                self.label.setAnchor((1, 0))

                # get the position of upper right corner of the visible area
                x = self.waveformPlot1.vb.viewRect().right()
                y = self.waveformPlot1.vb.viewRect().top()

                # calculate a small offset
                x_offset = self.waveformPlot1.viewRect().width() * 0.05
                y_offset = self.waveformPlot1.viewRect().height() * 0.2

                # set the position of the text
                self.label.setPos(x - x_offset, y + y_offset)

                
    def captureVisibleData(self):
        minX, maxX = self.region.getRegion()
        x = np.array(self.x)
        y = np.array(self.y)
        mask = (x >= minX) & (x <= maxX)
        x = x[mask]
        y = y[mask]

        event = {
            "type": "captureVisibleData",
            "x": x,
            "y": y
        }
        if self.onEvent is not None:
            self.onEvent(event)












        self.waveformPlot1.addItem(self.label)
