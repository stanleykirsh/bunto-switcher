def levenshtein_distance(s1, s2):
    # Создаем матрицу для хранения расстояний
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Инициализируем первую строку и столбец
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    # Заполняем матрицу
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                cost = 0
            else:
                cost = 1
            dp[i][j] = min(dp[i - 1][j] + 1,    # Удаление
                           dp[i][j - 1] + 1,    # Вставка
                           dp[i - 1][j - 1] + cost)  # Замена
    return dp[m][n]


def find_unique_correction(word, correct_words, max_distance=2):
    # Находим все подходящие варианты
    candidates = []
    for correct_word in correct_words:
        distance = levenshtein_distance(word, correct_word)
        if distance <= max_distance:
            candidates.append((correct_word, distance))

    # Сортируем по расстоянию и берем только уникальные варианты
    candidates.sort(key=lambda x: x[1])
    if len(candidates) == 1:
        return candidates[0][0]
    return None


# Пример использования
correct_words = ["зимний", "вена", "река", "рана", "зима", "зимник"]
word_with_typo = "римний"

correction = find_unique_correction(word_with_typo, correct_words)
if correction:
    print(
        f"Слово '{word_with_typo}' можно однозначно исправить на '{correction}'")
else:
    print(
        f"Не удалось найти однозначное исправление для слова '{word_with_typo}'")
