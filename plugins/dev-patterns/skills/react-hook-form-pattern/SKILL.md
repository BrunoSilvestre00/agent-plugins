---
name: react-hook-form-pattern
description: Convenção para formulários com react-hook-form, FormProvider e os componentes controlados do design system, incluindo formulários multi-etapa.
metadata:
  version: "0.1.0"
---

# Padrão de formulário (react-hook-form)

Use esta skill ao criar um formulário, single-step ou multi-step (wizard).

## Formulário simples

O componente "dono" do formulário chama `useForm()` e embrulha os campos em
`FormProvider`:

```tsx
const methods = useForm<MeuFormData>();

return (
  <FormProvider {...methods}>
    <form onSubmit={methods.handleSubmit(onSubmit)}>
      <MeusCampos />
      <Button type="submit">Enviar</Button>
    </form>
  </FormProvider>
);
```

## Campos: use `useFormContext`, nunca prop-drilling de `control`

Qualquer subcomponente do formulário pega o que precisa via `useFormContext()`
— não passe `control`/`errors` como prop manualmente por várias camadas:

```tsx
const { control, formState: { errors } } = useFormContext<MeuFormData>();
```

## Componentes do design system já são controlados

`InputText`, `Select`, `Checkbox` etc. de `components/common` já encapsulam
`Controller` por dentro — não use `register()` manual nem `Controller` direto
no código da view. Passe `control`, `name` e `rules` como props:

```tsx
<Select
  control={control}
  name="city"
  rules={{ required: 'Campo obrigatório' }}
  options={cityOptions}
/>
```

## Erros de campo

Renderize o erro manualmente logo abaixo do campo (é o padrão vigente no
projeto, mesmo que repetitivo):

```tsx
{errors.city && <S.ErrorText>{errors.city.message}</S.ErrorText>}
```

## Wizard multi-step

Cada etapa é uma view própria (ver `react-view-component-pattern`) que só usa
`useFormContext()` — o `useForm()`/`FormProvider` fica sempre no componente
container do wizard, nunca duplicado numa etapa.

## O que NÃO fazer

- `register()` manual num componente do design system — ele já faz isso.
- `Controller` direto na view, em vez de deixar o componente do design
  system encapsular.
- Passar `control`/`errors` como prop por várias camadas em vez de
  `useFormContext()`.
- Validação de CPF/telefone/cartão na mão — já existem utils prontos no
  projeto (`cpf-cnpj-validator`, `libphonenumber-js`, `card-validator`) para
  usar nas `rules`.
