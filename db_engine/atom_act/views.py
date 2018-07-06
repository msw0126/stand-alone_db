from atom_act.models import AtomAct
from atom_learn.models import AtomLearn
from common import ERRORS
from common.UTIL import auto_param, Response
from csv_reader.models import CsvReaderInfo

container_query_sql_lst = [
    "select a.*",
    "from db_model_iofieldtype a",
    "	INNER JOIN db_model_container b on a.project_id = b.project_id and a.component_id = b.container_id",
    "where a.project_id = '{project_id}'",
    "	and b.component_id = '{component_id}'"
]
container_fields_sql_lst = [
    "select a.*",
    "from db_model_iofieldtype a",
    "	INNER JOIN db_model_container b on a.project_id = b.project_id and a.component_id = b.container_id",
    "	INNER JOIN db_model_featurecombine c on b.project_id = c.project_id and b.component_id = c.robotx_spark_id",
    "where a.project_id = '{project_id}'",
    "	and c.component_id = '{component_id}'"
]

field_in_sql = "and a.field in ('{id}','{target}')"

combine_field_in_query = "\n".join(container_query_sql_lst + [field_in_sql])
container_fields_sql = "\n".join(container_fields_sql_lst)
# robotx_field_in_query = "\n".join(container_fields_sql + [field_in_sql])


@auto_param()
def load(request, project_id, component_id):
    db_field_types = AtomAct.objects.filter(project_id=project_id, component_id=component_id)
    if len(db_field_types) == 0:
        return Response.success()
    db_field_type = db_field_types[0]
        # return Response.fail(ERRORS.ATOM_ACT_NOT_CONFIGURED, None)
    result = dict(
        reason_code_nvars=db_field_type.reason_code_nvars,
        ncores=db_field_type.ncores
    )
    return Response.success(result)


@auto_param()
def saveInfo(request, project_id, component_id, atom_learn_id, input_comp_id,reason_code_nvars, ncores):
    try:
        if reason_code_nvars == "":
            return Response.fail(ERRORS.PARAMS_NOT_IS_NULL, None)
        ncores = 0 if ncores == "" else ncores
        atom_learn = AtomLearn.objects.filter(project_id=project_id, component_id=atom_learn_id)
        if len(atom_learn) == 0:
            return Response.fail(ERRORS.ATOM_LEARN_NOT_CONFIGURED, None)
        atom_learn = atom_learn[0]
        assert isinstance(atom_learn, AtomLearn)

        csv_reader = CsvReaderInfo.objects.filter(project_id=project_id, component_id=input_comp_id)
        if len(csv_reader) == 0:
            return Response.fail(ERRORS.CSV_READER_NOT_CONFIGURED, None)
        csv_reader = csv_reader[0]
        assert isinstance(csv_reader, CsvReaderInfo)

    # learn_input_type = extract_component_type(atom_learn.input_comp_id)
    # act_input_type = extract_component_type(input_comp_id)
    # feature_id = atom_learn.feature_id
    # if learn_input_type != act_input_type:
    #     return Response.success(ERRORS.COMPONENT_NOT_SAME_AS_ACT)

        AtomAct.objects.filter(project_id=project_id,component_id=component_id).delete()
        AtomAct(project_id=project_id,component_id=component_id,atom_learn_id=atom_learn_id,input_comp_id=input_comp_id,reason_code_nvars=reason_code_nvars,ncores=ncores).save()
        return Response.success()
    except UnicodeDecodeError as e:
        response = Response.fail(ERRORS.COMPONENT_NOT_SAME_AS_ACT, None)
        return response

        # @auto_param()
# def download_prediction(request, project_id, component_id, threshold=0.5):
#     prediction_path = AtomActExecutor.get_prediction_csv_local_path(project_id, component_id)
#     threshold = float(threshold)
#     response = Streamingfile_iterator(prediction_path, threshold))
#     response['Content-Type'] = 'application/octet-stream'
#     file_name = "%s_%s_%s" %(project_id, component_id, AtomActExecutor.PREDICTION_CSV)
#     response['Content-Disposition'] = 'attachment;filename="{0}"'.format(file_name)
#     return response



# @auto_param()
# def report(request, project_id, component_id):
#     res = dict()
#     for model_obj in MODEL_OBJECTS:
#         prop = model_obj.name
#         values = model_obj.cls.objects.filter(project_id=project_id, component_id=component_id)
#         if len(values) == 0:
#             if model_obj == ModelPredictionBIns:
#                 break
#             else:
#                 continue
#         value_lst = list()
#         for val in values:
#             value_lst.append({
#                 p: val.__getattribute__(p)
#                 for p in model_obj.props
#             })
#         res[prop] = value_lst
#     if len(res) == 0:
#         return Response.fail(ERRORS.NO_REPORT)
#     return Response.success(res)


class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

    def some_streaming_csv_view(request):
        """A view that streams a large CSV file."""
        # Generate a sequence of rows. The range is based on the maximum number of
        # rows that can be handled by a single sheet in most spreadsheet
        # applications.
        rows = (["Row {}".format(idx), str(idx)] for idx in range(65536))
        pseudo_buffer = Echo()
        # writer = csv.writer(pseudo_buffer)
        # response = StreamingHttpResponse((writer.writerow(row) for row in rows),
        #                                  content_type="text/csv")
        # response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
        # return response
