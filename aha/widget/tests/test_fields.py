# -*- coding: utf-8 -*-


from unittest import TestCase
import logging
log = logging.getLogger(__name__)
from formencode import validators, Invalid

from nose.tools import *
import formencode

from coregae.widget.field import *

class TestBasefield(TestCase):

    def test_basefield(self):
        """
        Test for functions of BaseFields
        """
        c = {'id':'AB1234', 'size':20}
        bf = TextField(name = 'foo', args = c)
        body = bf.render_body()
        
        assert_true( 'name = "foo"' in body)
        assert_true( 'id = "AB1234"' in body)

        body = bf.render_body(value = 'VALUESTRING')
        assert_true("VALUESTRING" in body)

        bf.title = 'THETITLE'
        assert_true("THETITLE" in bf.get_title())


    def test_validate(self):
        """
        Test for MediaHandler, validation
        """
        v = validators
        c = {'id':'AB1234', 'size':20}
        bf = TextField(name = 'foo', args = c, validator = v.Int())
        assert_equal(bf.validate('1')[0], 1)
        assert_equal(bf.validate('A')[0], None)

        # test for multiple validators
        bf = TextField(name = 'foo', args = c,
                     validator = ( v.Int(), v.OneOf([1, 2, 3]) ))
        assert_equal(bf.validate('1')[0], 1)
        assert_equal(bf.validate(2)[0], 2)
        assert_equal(bf.validate('A')[0], None)
        assert_equal(bf.validate('4')[0], None)
        assert_equal(bf.validate(10)[0], None)

        bf = TextField(name = 'foo', args = c,
                     validator = ( v.Int(), v.OneOf([1, 2, 3]), ),
                     required = True)

        r = bf.validate('')
        assert_equal(r[0], None)


    def test_fields(self):
        """
        Test for functions of subclass of BaseField
        """
        c = {'id':'AB1234', 'size':20}
        tf = TextField(name = 'foo', args = c)
        body = tf.render_body()
        assert_true( 'name = "foo"' in body)
        assert_true( 'id = "AB1234"' in body)

        hf = HiddenField(name = 'foo', args = c, default = 'defoo')

        body = hf.render_body(value = 'VALUESTRING')
        assert_true("VALUESTRING" in body)

        body = hf.render_body()
        assert_true("defoo" in body)

        rf = RadioField(name = 'foo', args = c,
                      values = (('vfoo', 'v1'), ('vbar', 'v2')))
        body = rf.render_body()
        for v in ('vfoo', 'vbar'):
            assert_true(">%s<" % v in body)
        for v in ('v1', 'v2'):
            assert_true("value = '%s'" % v in body)
        assert_true("checked" not in body)

        body = rf.render_body(value = 'v2')
        assert_true("checked" in body)

        cg = CheckboxGroup(name = 'foo', args = c,
                      values = (('vfoo', 'v1'), ('vbar', 1)))
        body = cg.render_body()
        for v in ('vfoo', 'vbar'):
            assert_true(">%s<" % v in body)
        for v in ('v1', '1'):
            assert_true('value = "%s"' % v in body)
        for v in ('v1', '1'):
            assert_true('name = "foo_%s"' % v in body)
        assert_true("checked" not in body)

        body = cg.render_body(value = 'v1')
        assert_true("checked" in body)

        body = cg.render_body(value = [1])
        assert_true("checked" in body)

        v = validators
        cg2 = CheckboxGroup(name = 'foo', args = c,
                      values = (('vfoo', 'v1'), ('vbar', 'v2')),
                      validator = v.Int())
        t = cg2.validate({'foo_v1':'1', 'foo_v2':'a', 'foo_g3':'b'})
        assert_equal(t[0][1], None)
        assert_true(isinstance(t[0][2], Invalid))

        t = cg2.validate({'foo_v1':'1', 'foo_v2':'2', 'foo_g3':'b'})
        assert_equal(sorted(t[0][1]), [1, 2])
        assert_equal(t[0][2], None)


        sf = SelectField(name = 'foo', args = c,
                      values = (('vfoo', 'v1'), ('vbar', 'v2')))
        body = sf.render_body()
        for v in ('vfoo', 'vbar'):
            assert_true("> %s </option>" % v in body)
        for v in ('v1', 'v2'):
            assert_true('value = "%s"' % v in body)
        assert_true("selected" not in body)

        body = sf.render_body(value = 'v2')
        assert_true("selected" in body)

        cf = CheckboxField(name = 'foo', args = c)
        body = cf.render_body()
        assert_true('name = "foo"' in body)
        cf = CheckboxField(name = 'foo')
        body = cf.render_body(value = True)
        assert_true("checked" in body)


        tf = TextArea(name = 'foo', args = c)
        body = tf.render_body()
        assert_true('name = "foo"' in body)
        body = tf.render_body(value = 'this is body<body>')
        assert_true(">this is body&lt;body&gt;<" in body)


        rt = RichText(name = 'foo', args = c)
        assert_equal(len(rt.get_objects()), 1)
        assert_equal(len(rt.get_object_tag()), 1)

        ff = FileField(name = 'foo')
        body = ff.render_body()
        assert_true('type = "file"' in body)
        assert_false('disabled' in body)

        body = ff.render_body('bar')
        assert_true(ff.REPLACE_PREFIX+'foo' in body)

        imgf = ImageField(name = 'foo')
        body = imgf.render_body(value = 'path/to/image')
        assert_true("path/to/image" in body)


        tf = TextField(name = 'foo', args = c, default = 'bar')
        body = tf.render_body()
        
        assert_true( 'value = "bar"' in body)


