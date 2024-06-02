num_classifiers = 25; %设定有多少个分类器
num_round = 1000; %设定循环次数

Fast_IST_time_list = [];
IST_time_list = [];

for prob = 0 : 100
Fast_IST_time = 0;
for repeat = 1 : 100
c = zeros(num_classifiers, 1); %min c'x
A = ones(1, num_classifiers); %Ax = b
b = 1; %Ax = b
B = 1; %Basic feasible solution
o = 0; %最优解的值
a = [1; zeros(num_classifiers - 1, 1)]; %a的解

clock1 = clock;
for num_training_data = 1 : num_round %训练数据个数

%更新训练数据
c = [c; -1; 0];
new = sign(rand(1, num_classifiers) - 1/2 + prob / 200); %新生成的预测数据
A = [A, zeros(num_training_data, 2); -new, zeros(1, 2 * (num_training_data-1)), -1, 1];
B = [B; num_classifiers + 2 * num_training_data];
b = [b; 0];

%整理单纯形
comb = [-A(num_training_data + 1, B(1 : num_training_data)), 1];
A(num_training_data + 1, :) = comb * A;
b(num_training_data + 1) = comb * b;

for iter = 1 : 2
pivot_row = 0;
pivot_column = 0;
max_increase = -1000;
%选择合适的行和列
for i = 1 : num_training_data + 1
if b(i) < -0.00001
min_factor = 1000;
min_factor_column = 0;
for j = 1 : 2 * num_training_data + num_classifiers
if A(i, j) < -0.00001
if min_factor > c(j) / A(i, j) - 0.00001
min_factor = c(j) / A(i, j);
min_factor_column = j;
end
end
end
if min_factor_column > 0
if max_increase < -min_factor * b(i) - 0.00001
max_increase = -min_factor * b(i);
pivot_column = min_factor_column;
pivot_row = i;
elseif max_increase < -min_factor * b(i) + 0.00001
if B(i) > B(pivot_row)
pivot_column = min_factor_column;
pivot_row = i;
end
end
end
end
end

if pivot_row > 0
if B(pivot_row) <= num_classifiers
a(B(pivot_row)) = 0;
end
B(pivot_row) = pivot_column;
factor = A(pivot_row, pivot_column);
A(pivot_row, :) = A(pivot_row, :) / factor;
b(pivot_row) = b(pivot_row) / factor;
if B(pivot_row) <= num_classifiers
a(B(pivot_row)) = b(pivot_row);
end
for i = 1 : num_training_data + 1
if i ~= pivot_row
factor = -A(i, pivot_column);
A(i, :) = A(i, :) + factor * A(pivot_row, :);
b(i) = b(i) + factor * b(pivot_row);
if B(i) <= num_classifiers
a(B(i)) = b(i);
end
end
end
factor = -c(pivot_column);
c = c + factor * A(pivot_row, :)';
o = o + factor * b(pivot_row);
else
break
end
end
end
clock2 = clock;
Fast_IST_time = Fast_IST_time + etime(clock2, clock1);
end
Fast_IST_time_list = [Fast_IST_time_list; Fast_IST_time / 100];
end

for prob = 0 : 100
IST_time = 0;
for repeat = 1 : 100
c = zeros(num_classifiers, 1); %min c'x
A = ones(1, num_classifiers); %Ax = b
b = 1; %Ax = b
B = 1; %Basic feasible solution
o = 0; %最优解的值
a = [1; zeros(num_classifiers - 1, 1)]; %a的解

clock1 = clock;
for num_training_data = 1 : num_round %训练数据个数

%更新训练数据
c = [c; -1; 0];
new = sign(rand(1, num_classifiers) - 1/2 + prob / 200); %新生成的预测数据
A = [A, zeros(num_training_data, 2); -new, zeros(1, 2 * (num_training_data-1)), -1, 1];
B = [B; num_classifiers + 2 * num_training_data];
b = [b; 0];

%整理单纯形
comb = [-A(num_training_data + 1, B(1 : num_training_data)), 1];
A(num_training_data + 1, :) = comb * A;
b(num_training_data + 1) = comb * b;

while true
pivot_row = 0;
pivot_column = 0;
max_increase = -1000;
%选择合适的行和列
for i = 1 : num_training_data + 1
if b(i) < -0.00001
min_factor = 1000;
min_factor_column = 0;
for j = 1 : 2 * num_training_data + num_classifiers
if A(i, j) < -0.00001
if min_factor > c(j) / A(i, j) - 0.00001
min_factor = c(j) / A(i, j);
min_factor_column = j;
end
end
end
if min_factor_column > 0
if max_increase < -min_factor * b(i) - 0.00001
max_increase = -min_factor * b(i);
pivot_column = min_factor_column;
pivot_row = i;
elseif max_increase < -min_factor * b(i) + 0.00001
if B(i) > B(pivot_row)
pivot_column = min_factor_column;
pivot_row = i;
end
end
end
end
end

if pivot_row > 0
if B(pivot_row) <= num_classifiers
a(B(pivot_row)) = 0;
end
B(pivot_row) = pivot_column;
factor = A(pivot_row, pivot_column);
A(pivot_row, :) = A(pivot_row, :) / factor;
b(pivot_row) = b(pivot_row) / factor;
if B(pivot_row) <= num_classifiers
a(B(pivot_row)) = b(pivot_row);
end
for i = 1 : num_training_data + 1
if i ~= pivot_row
factor = -A(i, pivot_column);
A(i, :) = A(i, :) + factor * A(pivot_row, :);
b(i) = b(i) + factor * b(pivot_row);
if B(i) <= num_classifiers
a(B(i)) = b(i);
end
end
end
factor = -c(pivot_column);
c = c + factor * A(pivot_row, :)';
o = o + factor * b(pivot_row);
else
break
end
end
end
clock2 = clock;
IST_time = IST_time + etime(clock2, clock1);
end
IST_time_list = [IST_time_list; IST_time / 100];
end

pic = plot(50 + [0 : 100]/2, [Fast_IST_time_list, IST_time_list], 'linewidth',2);
legend('Fast-IST', 'IST');
xlabel('Probability');
ylabel('Time/s');
set(gca,'fontsize',14);
set(pic(2), 'linestyle', '--');

