# Как быстро опубликовать репозиторий

1. Создать новый публичный репозиторий на GitHub, например `adas-scenarioguard`.
2. Распаковать архив с этим проектом.
3. В папке проекта выполнить:

```bash
git init
git add .
git commit -m "Initial MVP for ADAS ScenarioGuard"
git branch -M main
git remote add origin https://github.com/<username>/adas-scenarioguard.git
git push -u origin main
```

4. На сдачу отправить ссылку вида:

```text
https://github.com/<username>/adas-scenarioguard
```
