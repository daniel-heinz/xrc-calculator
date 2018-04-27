import wx
from wx import xrc
from validator import CalcValidator
from asteval import Interpreter
from converter import *


class CalculatorApp(wx.App):
    curr_conv = CurrencyConverter()
    dist_conv = DistanceConverter()
    speed_conv = SpeedConverter()
    res, frm = None, None
    calc_panel, conv_panel = None, None

    def OnInit(self):
        self.res = xrc.XmlResource('calculator.xrc')
        self.build_frame()
        return True

    def build_frame(self):
        frm = self.frm = self.res.LoadFrame(None, 'CalcFrame')
        calc_panel = self.calc_panel = xrc.XRCCTRL(frm, 'calc_panel')
        conv_panel = self.conv_panel = xrc.XRCCTRL(frm, 'conv_panel')

        def swap_panel_calc(evt):
            if conv_panel.IsShown():
                frm.SetTitle("wxCalculator")
                frm.SetSize((400, 300))
                calc_panel.Show()
                conv_panel.Hide()
                frm.Layout()

        def swap_panel_conv(evt):
            if calc_panel.IsShown():
                frm.SetTitle("wxCalculator [Converter]")
                frm.SetSize((600, 200))
                calc_panel.Hide()
                conv_panel.Show()
                frm.Layout()

        frm.Bind(wx.EVT_MENU, lambda e: frm.Close(), id=xrc.XRCID('mi_quit'))
        frm.Bind(wx.EVT_MENU, swap_panel_calc, id=xrc.XRCID('mi_calc'))
        frm.Bind(wx.EVT_MENU, swap_panel_conv, id=xrc.XRCID('mi_conv'))

        self.bind_calc()
        self.bind_conv()
        frm.Show()

    def bind_calc(self):
        display = xrc.XRCCTRL(self.calc_panel, 'tctrl_calc_in')
        display.Validator = CalcValidator()
        enter_id, num_enter_id = wx.NewId(), wx.NewId()
        clear_id = wx.NewId()
        accelerator_tbl = wx.AcceleratorTable([
            (wx.ACCEL_NORMAL, wx.WXK_RETURN, enter_id), (wx.ACCEL_NORMAL, wx.WXK_NUMPAD_ENTER, num_enter_id),
            (wx.ACCEL_NORMAL, wx.WXK_DELETE, clear_id)
        ])
        self.calc_panel.SetAcceleratorTable(accelerator_tbl)

        def handle_key_press(this, event):
            if event.GetId() == enter_id or event.GetId() == num_enter_id:
                exec_calc(this)
            elif event.GetId() == clear_id:
                update_screen()

        # Number buttons
        self.calc_panel.Bind(wx.EVT_BUTTON, lambda e: update_screen('0'), id=xrc.XRCID('btn_zero'))
        self.calc_panel.Bind(wx.EVT_BUTTON, lambda e: update_screen('1'), id=xrc.XRCID('btn_one'))
        self.calc_panel.Bind(wx.EVT_BUTTON, lambda e: update_screen('2'), id=xrc.XRCID('btn_two'))
        self.calc_panel.Bind(wx.EVT_BUTTON, lambda e: update_screen('3'), id=xrc.XRCID('btn_three'))
        self.calc_panel.Bind(wx.EVT_BUTTON, lambda e: update_screen('4'), id=xrc.XRCID('btn_four'))
        self.calc_panel.Bind(wx.EVT_BUTTON, lambda e: update_screen('5'), id=xrc.XRCID('btn_five'))
        self.calc_panel.Bind(wx.EVT_BUTTON, lambda e: update_screen('6'), id=xrc.XRCID('btn_six'))
        self.calc_panel.Bind(wx.EVT_BUTTON, lambda e: update_screen('7'), id=xrc.XRCID('btn_seven'))
        self.calc_panel.Bind(wx.EVT_BUTTON, lambda e: update_screen('8'), id=xrc.XRCID('btn_eight'))
        self.calc_panel.Bind(wx.EVT_BUTTON, lambda e: update_screen('9'), id=xrc.XRCID('btn_nine'))

        # Function buttons
        self.calc_panel.Bind(wx.EVT_BUTTON, lambda e: update_screen('.'), id=xrc.XRCID('btn_comma'))
        self.calc_panel.Bind(wx.EVT_BUTTON, lambda e: update_screen('+'), id=xrc.XRCID('btn_add'))
        self.calc_panel.Bind(wx.EVT_BUTTON, lambda e: update_screen('-'), id=xrc.XRCID('btn_sub'))
        self.calc_panel.Bind(wx.EVT_BUTTON, lambda e: update_screen('*'), id=xrc.XRCID('btn_mult'))
        self.calc_panel.Bind(wx.EVT_BUTTON, lambda e: update_screen('/'), id=xrc.XRCID('btn_div'))
        self.calc_panel.Bind(wx.EVT_BUTTON, lambda e: update_screen('**'), id=xrc.XRCID('btn_pow'))
        self.calc_panel.Bind(wx.EVT_BUTTON, lambda e: update_screen('sqrt(x)'), id=xrc.XRCID('btn_sqrt'))
        self.calc_panel.Bind(wx.EVT_BUTTON, lambda e: update_screen('(x+y)'), id=xrc.XRCID('btn_brackets'))
        self.calc_panel.Bind(wx.EVT_BUTTON, lambda e: update_screen(), id=xrc.XRCID('btn_ca'))
        self.calc_panel.Bind(wx.EVT_BUTTON, lambda e: exec_calc(self), id=xrc.XRCID('btn_equals'))
        self.calc_panel.Bind(wx.EVT_MENU, lambda e: handle_key_press(self, e), id=enter_id, id2=num_enter_id)
        self.calc_panel.Bind(wx.EVT_MENU, lambda e: handle_key_press(self, e), id=clear_id)

        def update_screen(symbol=None):
            if not display.IsEmpty() and symbol == 'sqrt(x)':
                content = display.GetLineText(0)
                display.Clear()
                display.AppendText('sqrt({0})'.format(content))
            elif not display.IsEmpty() and symbol == '(x+y)':
                content = display.GetLineText(0)
                display.Clear()
                display.AppendText('({0})'.format(content))
            elif symbol:
                display.AppendText(symbol)
            else:
                display.Clear()

        def exec_calc(this):
            if not display.IsEmpty():
                a_eval = Interpreter()
                res = str(a_eval(display.GetLineText(0)))

                if len(a_eval.error) > 0:
                    err = a_eval.error[0].get_error()
                    err_box = wx.RichMessageDialog(
                        this.frm, 'An {0} occurred. Pleas check below for details.'.format(err[0]),
                        'Evaluation Error', wx.OK | wx.ICON_ERROR
                    )
                    err_list = [str(e.get_error()[1]).strip() + '\n' for e in a_eval.error]
                    err_box.ShowDetailedText(' '.join(err_list))
                    err_box.ShowModal()
                    display.SetBackgroundColour("pink")
                    display.SetFocus()
                    display.Refresh()
                else:
                    display.SetBackgroundColour(
                        wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
                    display.Refresh()
                    display.Clear()
                    display.AppendText(res)

    def bind_conv(self):
        cp = self.conv_panel
        curr_a, curr_b = xrc.XRCCTRL(cp, 'cmb_curr_a'), xrc.XRCCTRL(cp, 'cmb_curr_b')
        curr_av, curr_bv = xrc.XRCCTRL(cp, 'tctrl_curr_a'), xrc.XRCCTRL(cp, 'tctrl_curr_b')
        dist_a, dist_b = xrc.XRCCTRL(cp, 'cmb_dist_a'), xrc.XRCCTRL(cp, 'cmb_dist_b')
        dist_av, dist_bv = xrc.XRCCTRL(cp, 'tctrl_dist_a'), xrc.XRCCTRL(cp, 'tctrl_dist_b')
        speed_a, speed_b = xrc.XRCCTRL(cp, 'cmb_speed_a'), xrc.XRCCTRL(cp, 'cmb_speed_b')
        speed_av, speed_bv = xrc.XRCCTRL(cp, 'tctrl_speed_a'), xrc.XRCCTRL(cp, 'tctrl_speed_b')
        currencies = list(
            ['{0}, {1} ({2})'.format(k.ljust(4), v['Country'], v['Symbol']) for k, v in
             self.curr_conv.get_supported().items()]
        )
        distances = list(['{0} ({1})'.format(k.ljust(4), v['Name'])
                          for k, v in self.dist_conv.get_supported().items()])
        speeds = list(['{0} ({1})'.format(k.ljust(4), v['Name'])
                       for k, v in self.speed_conv.get_supported().items()])

        curr_a.SetItems(currencies)
        curr_a.Select(0)
        curr_b.SetItems(currencies)
        curr_b.Select(1)

        dist_a.SetItems(distances)
        dist_a.Select(0)
        dist_b.SetItems(distances)
        dist_b.Select(1)

        speed_a.SetItems(speeds)
        speed_a.Select(0)
        speed_b.SetItems(speeds)
        speed_b.Select(1)

        def ltr_convert(cmb_a, cmb_b, tctrl_a, tctrl_b, converter: ConverterBase):
            unit_a = cmb_a.GetValue().split(' ', 1)[0]
            unit_b = cmb_b.GetValue().split(' ', 1)[0]
            try:
                value = float(tctrl_a.GetValue())
                tctrl_b.ChangeValue(str(round(converter.convert(unit_a, unit_b, value), 4)))
            except ValueError as e:
                print(e)

        def rtl_convert(cmb_a, cmb_b, tctrl_a, tctrl_b, converter: ConverterBase):
            unit_a = cmb_a.GetValue().split(' ', 1)[0]
            unit_b = cmb_b.GetValue().split(' ', 1)[0]
            try:
                value = float(tctrl_b.GetValue())
                tctrl_a.ChangeValue(str(round(converter.convert(unit_b, unit_a, value), 4)))
            except ValueError as e:
                print(e)

        def l_curr_cmb_ch(converter: ConverterBase):
            unit_a = curr_a.GetValue()[0:3]
            unit_b = curr_b.GetValue()[0:3]
            try:
                xrc.XRCCTRL(cp, 'tctrl_exchange').ChangeValue(
                    str(round(converter.conversion_rate(unit_a, unit_b), 4)))
            except ValueError:
                pass

        def r_curr_cmb_ch(converter: ConverterBase):
            unit_a = curr_a.GetValue()[0:3]
            unit_b = curr_b.GetValue()[0:3]
            try:
                xrc.XRCCTRL(cp, 'tctrl_exchange').ChangeValue(
                    str(round(converter.conversion_rate(unit_b, unit_a), 4)))
            except ValueError:
                pass

        l_curr_cmb_ch(self.curr_conv)
        curr_a.Bind(wx.EVT_COMBOBOX, lambda e: l_curr_cmb_ch(self.curr_conv))
        curr_b.Bind(wx.EVT_COMBOBOX, lambda e: r_curr_cmb_ch(self.curr_conv))
        curr_av.Bind(wx.EVT_TEXT, lambda e: ltr_convert(curr_a, curr_b, curr_av, curr_bv, self.curr_conv))
        curr_bv.Bind(wx.EVT_TEXT, lambda e: rtl_convert(curr_a, curr_b, curr_av, curr_bv, self.curr_conv))
        cp.Bind(wx.EVT_BUTTON, lambda e: ltr_convert(curr_a, curr_b, curr_av, curr_bv, self.curr_conv))
        cp.Bind(wx.EVT_BUTTON, lambda e: self.curr_conv.try_update_exchange(), id=xrc.XRCID('btn_refresh'))

        dist_a.Bind(wx.EVT_COMBOBOX, lambda e: ltr_convert(dist_a, dist_b, dist_av, dist_bv, self.dist_conv))
        dist_b.Bind(wx.EVT_COMBOBOX, lambda e: ltr_convert(dist_a, dist_b, dist_av, dist_bv, self.dist_conv))
        dist_av.Bind(wx.EVT_TEXT, lambda e: ltr_convert(dist_a, dist_b, dist_av, dist_bv, self.dist_conv))
        dist_bv.Bind(wx.EVT_TEXT, lambda e: rtl_convert(dist_a, dist_b, dist_av, dist_bv, self.dist_conv))

        speed_a.Bind(wx.EVT_COMBOBOX, lambda e: ltr_convert(speed_a, speed_b, speed_av, speed_bv, self.speed_conv))
        speed_b.Bind(wx.EVT_COMBOBOX, lambda e: ltr_convert(speed_a, speed_b, speed_av, speed_bv, self.speed_conv))
        speed_av.Bind(wx.EVT_TEXT, lambda e: ltr_convert(speed_a, speed_b, speed_av, speed_bv, self.speed_conv))
        speed_bv.Bind(wx.EVT_TEXT, lambda e: rtl_convert(speed_a, speed_b, speed_av, speed_bv, self.speed_conv))


if __name__ == "__main__":
    app = CalculatorApp(False)
    app.MainLoop()
