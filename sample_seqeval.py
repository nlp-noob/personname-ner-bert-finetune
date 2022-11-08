from seqeval.metrics import accuracy_score, precision_score, recall_score, f1_score
from seqeval.metrics import classification_report
y_true = [['O', 'O', 'O', 'B-MISC', 'I-MISC', 'I-MISC', 'O'], ['B-PER', 'I-PER', 'O']]
y_pred = [['O', 'O', 'B-MISC', 'I-MISC', 'I-MISC', 'I-MISC', 'O'], ['B-PER', 'I-PER', 'O']]
y_true = [['B-PER', 'O', 'I-PER']]
y_pred = [['B-PER', 'O', 'I-PER']]

print(f'\t\t准确率为： {accuracy_score(y_true, y_pred)}')
print(f'\t\t查准率为： {precision_score(y_true, y_pred)}')
print(f'\t\t召回率为： {recall_score(y_true, y_pred)}')
print(f'\t\tf1值为： {f1_score(y_true, y_pred)}')
print(classification_report(y_true, y_pred))
