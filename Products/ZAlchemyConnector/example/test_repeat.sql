INSERT INTO test_table(id, name, description)
VALUES
<tal:block tal:condition="python: context.check('iter_tests')" tal:repeat="i python: context.get('iter_tests')">
    (
        <tal:block tal:replace="python: ':id_{}'.format(repeat['i'].index)"></tal:block>,
        <tal:block tal:replace="python: ':name_{}'.format(repeat['i'].index)"></tal:block>,
        <tal:block tal:replace="python: ':description_{}'.format(repeat['i'].index)" ></tal:block>

    )<tal:block tal:condition="not: repeat/i/end">,</tal:block>
</tal:block>
;
