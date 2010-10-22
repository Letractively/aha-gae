# -*- coding: utf-8 -*-


from unittest import TestCase
import logging
log = logging.getLogger(__name__)
from formencode import validators, Invalid



from nose.tools import *


from coregae.widget.forms import(FieldHolder, BaseForm, Fieldset,
                                 SelectiveFieldset, Form,
                                 RootTabbedFieldset)
from coregae.widget.field import *


class TestBaseform(TestCase):

    def test_baseform1(self):
        """
        Test for BaseForm
        """
        class TmpForm(FieldHolder):
            name1 = TextField()
            name2 = TextField()

        tf = TmpForm()
        assert_equal(tf[0].get_name(), 'name1')
        assert_equal(tf[1].get_name(), 'name2')
        assert_equal(tf['name1'], tf[0])
        assert_equal(tf['name2'], tf[1])

        assert_raises(IndexError, tf.__getitem__, 2)
        assert_raises(KeyError, tf.__getitem__, 'name3')

        assert_equal(tf[:1], [tf[0]])
        assert_equal(tf[:], [tf[0], tf[1]])
        assert_equal(tf[::-1], [tf[1], tf[0]])

        i = iter(tf)
        assert_equal(i.next(), tf[0])
        assert_equal(i.next(), tf[1])

        assert_equal(len(tf), 2)

    def test_baseform2(self):
        """
        Test for BaseForm
        """
        from formencode import validators

        class TmpForm(BaseForm):
            name1 = TextField(validator = validators.Int())
            name2 = TextField(validator = validators.Email())
            action = 'foo'
            multipart = True

        tf = TmpForm(submit = "ookei", clear = "klear", clas = 'hoge')
        fb = tf.render()
        assert_true("name1" in fb)
        assert_true("name2" in fb)
        assert_true("ookei" in fb)
        assert_true("klear" in fb)
        assert_true("multipart/form-data" in fb)

        tf = TmpForm(submit = "", clear = "", clas = "form_class")
        fb = tf.render()
        assert_true("ookei" not in fb)
        assert_true("klear" not in fb)
        assert_true("form_class" in fb)

        assert_equal(tf.validate({'name1':'123'}), {})
        assert_equal(tf.validate({'name2':'hoge@hoge.com'}), {})
        assert_equal(tf.validate({'name1':'A'}).keys(), ['name1'])
        assert_equal(sorted(tf.validate({'name1':'A', 'name2':'A'}).keys()),
                                         sorted(['name1', 'name2']))
        assert_equal(tf.validate({'name1':'1', 'name2':'A'}).keys(), ['name2'])

        tf.validate({'name1':'123'})
        assert_equal(tf.validate_result['name2'], None)

        tf.validate({'name2':'123'}, {'name1':'abcde'})
        assert_true('name1' in tf.validate_result)



        # Checking for attributes
        assert_equal(tf.action, 'foo')

        tf2 = TmpForm(action = 'bar')
        assert_equal(tf2.action, 'bar')


    def test_fieldset1(self):
        """
        Test for Fieldset
        """
        class TmpForm(FieldHolder):
            name1 = TextField()
            fieldset1 = Fieldset(title = "foo title 1",
                    fields = (
                        TextField(name = 'name1-1'),
                        TextField(name = 'name1-2')
                        ) )
            name2 = TextField()
            fieldset2 = Fieldset(title = "foo title 2",
                    fields = (
                        TextField(name = 'name2-1'),
                        TextField(name = 'name2-2')
                        ) )

        tf = TmpForm()
        """
        print len(tf.fields)
        print tf.fields
        print "*"*40
        print tf[:]
        """

        assert_equal(tf[0].get_name(), 'name1')
        assert_equal(tf[2].get_name(), 'name1-1')
        assert_equal(tf[4].get_name(), 'name2')
        assert_equal(tf[5].get_name(), 'fieldset2')
        assert_equal(tf[6].get_name(), 'name2-1')

        assert_equal(tf['name1'].get_name(), 'name1')
        assert_equal(tf['name1-1'].get_name(), 'name1-1')
        assert_equal(tf['fieldset2'].get_name(), 'fieldset2')
        assert_equal(tf['name2-1'].get_name(), 'name2-1')

        # test for replacing field by using index
        tf2 = TmpForm()
        tf2[0] = TextArea(name = 'name1')
        assert_true(isinstance(tf2[0], TextArea))
        tf2[2] = TextArea(name = 'name1-1')
        assert_true(isinstance(tf2[2], TextArea))

        tf2['name2'] = TextArea(name = 'name2')
        assert_true(isinstance(tf2['name2'], TextArea))
        assert_true(isinstance(tf2[4], TextArea))

        tf2['name2-2'] = TextArea(name = 'name2-2')
        assert_true(isinstance(tf2['name2-2'], TextArea))
        assert_true(isinstance(tf2[7], TextArea))

        # append new field at the end of the field
        tf2['name3'] = TextArea(name = 'name3')
        assert_true(isinstance(tf2['name3'], TextArea))
        assert_true(tf2.fields[-1][0], 'name3')
        assert_equal(len(tf2[:]), 9)

        tf2 = tf2+TextArea(name = 'name4')
        assert_true(isinstance(tf2['name4'], TextArea))
        assert_true(tf2.fields[-1][0], 'name4')

        tf2+= TextArea(name = 'name5')
        assert_true(isinstance(tf2['name5'], TextArea))
        assert_true(tf2.fields[-1][0], 'name5')


    def test_media1(self):
        """
        Test for From, handling media
        """
        from formencode import validators

        class TmpForm(BaseForm):
            name1 = TextField()
            fieldset1 = Fieldset(title = "foo title 1",
                    fields = (
                        TextField(name = 'name1-1',
                        objects = (('foo.css', 'text/css'),
                                 ('bar.css', 'text/javascript')) ),
                        RichText(name = 'name1-2')
                        ) )
            name2 = TextField()
            fieldset2 = Fieldset(title = "foo title 2",
                    fields = (
                        TextField(name = 'name2-1'),
                        TextField(name = 'name2-2')
                        ) )
            name3 = RichText()

        tf = TmpForm()

        assert_equal(len(tf.get_objects()), 4)
        assert_equal(len(tf.get_objects('text/css')), 2)
        assert_true(('foo.css', 'text/css') in tf.get_objects('text/css'))


    def test_selectivefieldset(self):
        """
        Test for SelectiveFieldset
        """
        v = validators

        class TmpForm(Form):
            name1 = TextField()
            fieldset1 = SelectiveFieldset(title = "foo title 1",
                    innerfields = (
                      ( 'if1', 'innerfield1',
                       (TextField(name = 'name1-1', validator = v.Int()),
                        TextField(name = 'name1-2') ) ),
                      ( 'if2', 'innerfield2',
                       (TextField(name = 'name2-1'),
                        TextField(name = 'name2-2') ) ),
                      ( 'if3', 'innerfield3', () ),
                      ) )
            name2 = TextField()

        tf = TmpForm()
        fb = tf.render()
        assert_true("if2__name2-1" in fb)
        assert_equal(tf.validate({'fieldset1':'if1', 'if1__name1-1': '1'}), {})
        r = tf.validate({'fieldset1':'if1', 'if1__name1-1': 'a'})
        assert_true(isinstance(r['if1__name1-1'], Invalid))

        tf = TmpForm()
        fb = tf.render({'fieldset1':
                "{'_selection':'if1', 'name1-1':'1', 'name1-2':'foo'}"})
        assert_true(fb, "name = 'if1__name1-1' id = 'if1__name1-1_id' value = '1'")


    def test_item_deletion(self):
        """
        Test for BaseForm
        """
        class TmpForm(FieldHolder):
            name1 = TextField()
            name2 = TextField()
            name3 = TextField()

        del TmpForm['name3']
        tf = TmpForm()
        assert_equal( sorted(x[0] for x in tf.get_items()), ['name1', 'name2'] )

    def test_item_reassignment(self):
        """
        Test for BaseForm
        """
        class TmpForm(FieldHolder):
            name1 = TextField()
            name2 = TextField()
            name3 = TextField()

        TmpForm['name3'] = TextArea()
        tf = TmpForm()
        assert_true( isinstance(tf['name3'], TextArea) )



    def test_tabbedfieldset(self):
        """
        Test for Tabbed Fieldset
        """
        v = validators

        class TmpForm(Form):
            name1 = TextField()
            fieldset1 = RootTabbedFieldset(title = "foo title 1", name = 'foo name',
                innerfields = (
                        ('tab1',
                        (
                        TextField(name = 'name1-1', validator = v.Int()),
                        TextField(name = 'name1-2') ),
                        ),
                        ('tab2',
                        (
                        TextField(name = 'name2-1', validator = v.Int()),
                        TextField(name = 'name2-2') ),
                        ),
                        ('tab3',
                        (
                        TextField(name = 'name3-1', validator = v.Int()),
                        TextField(name = 'name3-2') ),
                        )
                      ),
                )

        tf = TmpForm()
        fb = tf.render()
        #print fb
        assert_equal(tf.validate({'fieldset1':'if1', 'if1__name1-1': '1'}), {})
        r = tf.validate({'fieldset1':'if1', 'name1-1': 'a'})
        print r
        assert_true(isinstance(r['name1-1'], Invalid))

        tf = TmpForm()
        fb = tf.render({'fieldset1':
                "{'_selection':'if1', 'name1-1':'1', 'name1-2':'foo'}"})
        assert_true(fb, "name = 'if1__name1-1' id = 'if1__name1-1_id' value = '1'")


